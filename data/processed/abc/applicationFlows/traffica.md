---
document_owner: "Intra team"
systems_involved:
  - Traffica
  - SFTP
  - Hive
  - Impala
  - HDFS
  - Grafana
scheduling:
  - Java Spring Boot
data_sources:
  - trafficaftp@cne.def.gr:/data/1/trafficaftp/Traffica_XDR
target_tables:
  - sai.sms_load
  - sai.sms_raw_text
  - sai.sms_raw
  - sai.voice_load
  - sai.voice_raw_text
  - sai.voice_raw_text_c2c
  - sai.voice_raw
scripts_location: "/shared/abc/traffica"
hdfs_paths:
  - /ez/warehouse/sai.db/landing_zone/sms
  - /ez/warehouse/sai.db/landing_zone/voice
responsible_users:
  - traffica
monitored: true
alerts_handling: "Email alerts on failure; Grafana dashboard for monitoring error metrics"
summary: >
  This document describes the Traffica data ingestion flows for SMS and VOICE XDR files. 
  It includes file retrieval via SFTP, local and HDFS staging, table loading to Hive and Impala, 
  cleanup logic, scheduling via Spring Boot, monitoring via Grafana, and alerting via email notifications.
tags:
  - traffica
  - traffica_sms
  - traffica_voice
  - sms xdr flow
  - voice xdr flow
  - sftp ingestion
  - springboot scheduler
  - hive landing zone
  - impala raw table
  - hdfs staging
  - bigstreamer ingestion
  - .LOADED suffix
  - grafana monitoring
  - xdr pipeline
  - application pause resume
---
# Traffica Flow
## Useful links
- [Wiki](https://metis.ghi.com/obss/bigdata/abc/etl/traffica/traffica-devops/-/wikis/home)
- [Infrastructure](https://metis.ghi.com/obss/bigdata/abc/etl/traffica/traffica-devops/-/wikis/Infrastructure)
## SMS Flow
> The SMS flow ingests XDR files from the remote SFTP server, stages them on the local disk and HDFS, 
> loads them into Hive staging tables, and inserts them into the final Impala table.
``` mermaid
     graph TD
      A0["abc Flow <br> User: trafficaftp"]
      A1["Host: cne.def.gr <br> Path: /data/1/trafficaftp/Traffica_XDR"]
      A2["Staging Directory <br> Path: /data/1/traffica_LZ/sms"]
      A3("Staging HDFS Directory <br> Path: /ez/warehouse/sai.db/landing_zone/sms")
      A4("Staging Table <br> Hive: sai.sms_load")
      A5("Staging Table <br> Hive: sai.sms_raw_text")
      A6("Table <br> Impala: sai.sms_raw")
      A7("Cleanup <br> Add .LOADED suffix to local raw files <br> Clean local staging directories <br> Clean HDFS tables/directories")
    
      A0 -->|SFTP| A1
      A1 --> |Merge files| A2
      A2 --> |HDFS Load| A3
      A3 --> |Hive Load| A4
      A4 --> |Hive Insert| A5
      A5 --> |Impala Insert| A6
      A6 --> |Successful loaded files only| A7
```
**Flow Summary:**
- SFTP pull from cne.def.gr to local staging
- Local merge and upload to HDFS
- Load to Hive staging tables
- Insert into Impala target table
- Cleanup: Add `.LOADED` suffix to processed files and clean staging dirs
**Schedule**: `every 35 minutes`  
**Scheduler**: `Java Springboot Application`  
**User**: `traffica`  
**Active Node**: `unc2.bigdata.abc.gr`  
**Backup Node**: `unc1.bigdata.abc.gr`  
**Installation directory**: `/shared/abc/traffica`  
**Logs**: `/shared/abc/traffica/logs`  
**Configuration File**: `/shared/abc/traffica/config/application.yml`
**Start command**: `supervisorctl start traffica_sms`  
**Stop command**: `supervisorctl stop traffica_sms`  
**Enable command (un-pause)**: `curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/enable"`
**Alerts**:
- Mail with subject: `Traffica Application failed`
Possible messages:
1. `Traffica sms main flow failed.`
2. `Traffica sms application has been paused due to multiple sequential failures. Manual actions are needed.`
3. `Traffica sms application has been paused due to inability to rename local files. Manual actions are needed.`
4. `Traffica sms application has been paused due to inability to clean up files. Manual actions are needed.`
**Troubleshooting steps**:
- Check to see if the application is running:
  From `unc2` with personal account:
  ``` bash
  curl -X GET "http://unc2.bigdata.abc.gr:11482/traffica/app/info/check"
  ```
- Check the logs for errors to identify the root cause
  From `unc2` as `traffica`:
  ``` bash
  # For the current log file
  grep -i -e error -e exception /shared/abc/traffica/logs/traffica-sms.log
  # For older compressed files
  zgrep -i -e error -e exception /shared/abc/traffica/logs/<yearMonthFolder>/<name_of_logfile>
  ```
- Check metrics and error rates from Grafana
  Open Firefox using VNC and go to `https://unc1.bigdata.abc.gr:3000/d/qIM5rod4z/traffica`
  Use panels ending in `Err` to identify problematic components and steps.
  Use `Files`,`Size`,`Rows` to identify if input has changed
- If there is a problem renaming files with the `.LOADED` suffix
  From `unc2` as `traffica`:
  ``` bash
  # Get files that where processed correctly
  grep 'filelist=' /shared/abc/traffica/logs/traffica-sms.log 
  # Move files pending rename from the list above
  cd /data/1/trafficaftp/Traffica_XDR
  mv <file>{,.LOADED}
  ```
- If the root cause is resolved resume normal operation.
  The flow has been designed with auto-recovery. It marks only successfully loaded files as `.LOADED` and handles/cleans up all staging directories on each run.
  From `unc2` with personal user:
  ``` bash
  # Check if scheduling is enabled 
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/disabled"
  # If the above command returns true
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/enable"
  ```
  - If `unc2` is down, then manually start the application on `unc1` this requires that VIP `cne.def.gr` has been migrated and SFTP is working on `unc1`
**Ndefs**:
  From `unc2` with personal account:
  ``` bash
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/info/health" # HTTP 200 if app is up
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/info/check" # returns message if up
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/shutdown/gracefully" # shutdown application. If flow is running, then wait to finish. App should terminate ONLY with this method.
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/disable" # enable flow scheduling
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/enable" # enable flow scheduling
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/disabled" # true if disabled, else false
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/cleanup/all" # Run cleanup on demand
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/main/run" # Run flow on demand
  # UI with endpoints available from VNC: http://unc2.bigdata.abc.gr:11483/traffica/swagger-ui/index.html#/
  ```
## Voice Flow
> The Voice flow processes CDR files similarly to SMS, but includes two Hive staging tables before 
> merging everything into the final Impala voice table.
``` mermaid
     graph TD
      A0["abc Flow <br> User: trafficaftp"]
      A1["cne.def.gr <br> Path: /data/1/trafficaftp/Traffica_XDR"]
      A2["Staging Directory <br> Path: /data/1/traffica_LZ/voice"]
      A3("Staging HDFS Directory <br> Path: /ez/warehouse/sai.db/landing_zone/voice")
      A4("Staging Table <br> Hive: sai.voice_load")
      A5("Staging Table <br> Hive: sai.voice_raw_text")
      A6("Staging Table <br> Hive: sai.voice_raw_text_c2c")
      A7("Table <br> Impala: sai.voice_raw")
      A8("Cleanup <br> Add .LOADED suffix to local raw files <br> Clean local staging directories <br> Clean HDFS tables/directories")
    
      A0 -->|SFTP| A1
      A1 --> |Merge files| A2
      A2 --> |HDFS Load| A3
      A3 --> |Hive Load| A4
      A4 --> |Hive Insert| A5
      A4 --> |Hive Insert| A6
      A5 --> |Impala Insert| A7
      A6 --> |Impala Insert| A7
      A7 --> |Successful loaded files only| A8
```
**Flow Summary:**
- SFTP pull from cne.def.gr to local staging
- Merge and stage to HDFS
- Load to two Hive raw text tables (voice_raw_text, voice_raw_text_c2c)
- Insert into final Impala voice_raw table
- Cleanup: Mark files as `.LOADED`, clean Hive + HDFS staging dirs
**Schedule**: `every 20 minutes`  
**Scheduler**: `Java Springboot Application`  
**User**: `traffica`  
**Active Node**: `unc2.bigdata.abc.gr`
**Backup Node**: `unc1.bigdata.abc.gr`
**Installation directory**: `/shared/abc/traffica`
**Logs**: `/shared/abc/traffica/logs`
**Configuration File**: `/shared/abc/traffica/config/application.yml`
**Start command**: `supervisorctl start traffica_voice`  
**Stop command**: `supervisorctl stop traffica_voice`  
**Enable command (un-pause)**: `curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/enable"`
**Alerts**:
- Mail with subject: `Traffica Application failed`
Possible messages:
1. `Traffica voice main flow failed.`
2. `Traffica voice application has been paused due to multiple sequential failures. Manual actions are needed.`
3. `Traffica voice application has been paused due to inability to rename local files. Manual actions are needed.`
4. `Traffica voice application has been paused due to inability to clean up files. Manual actions are needed.`
**Troubleshooting steps**:
- Check to see if the application is running:
  From `unc2` with personal account:
  ``` bash
  curl -X GET "http://unc2.bigdata.abc.gr:11482/traffica/app/info/check"
  ```
- Check the logs for errors to identify the root cause
  From `unc2` as `traffica`:
  ``` bash
  # For the current log file
  grep -i -e error -e exception /shared/abc/traffica/logs/traffica-voice.log
  # For older compressed files
  zgrep -i -e error -e exception /shared/abc/traffica/logs/<yearMonthFolder>/<name_of_logfile>
  ```
- Check metrics and error rates from Grafana
  Open Firefox using VNC and go to `https://unc1.bigdata.abc.gr:3000/d/qIM5rod4z/traffica`
  Use panels ending in `Err` to identify problematic components and steps.
  Use `Files`,`Size`,`Rows` to identify if input has changed
- If there is a problem renaming files with the `.LOADED` suffix
  From `unc2` as `traffica`:
  ``` bash
  # Get files that where processed correctly
  grep 'filelist=' /shared/abc/traffica/logs/traffica-voice.log 
  # Move files pending rename from the list above
  cd /data/1/trafficaftp/Traffica_XDR
  mv <file>{,.LOADED}
  ```
- If the root cause is resolved resume normal operation.
  The flow has been designed with auto-recovery. It marks only successfully loaded files as `.LOADED` and handles/cleans up all staging directories on each run.
  From `unc2` with personal user:
  ``` bash
  # Check if scheduling is enabled 
  curl -X GET "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/disabled"
  # If the above command returns true
  curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/enable"
  ```
  - If `unc2` is down, then manually start the application on `unc1` this requires that VIP `cne.def.gr` has been migrated and SFTP is working on `unc1`
**Ndefs**:
  From `unc2` with personal account:
  ``` bash
  curl -X GET "http://unc2.bigdata.abc.gr:11482/traffica/app/info/health" # HTTP 200 if app is up
  curl -X GET "http://unc2.bigdata.abc.gr:11482/traffica/app/info/check" # returns message if up
  curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/shutdown/gracefully" # shutdown application. If flow is running, then wait to finish. App should terminate ONLY with this method.
  curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/disable" # enable flow scheduling
  curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/enable" # enable flow scheduling
  curl -X GET "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/disabled" # true if disabled, else false
  curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/cleanup/all" # Run cleanup on demand
  curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/main/run" # Run flow on demand
  # UI with endpoints available from VNC: http://unc2.bigdata.abc.gr:11482/traffica/swagger-ui/index.html#/
```