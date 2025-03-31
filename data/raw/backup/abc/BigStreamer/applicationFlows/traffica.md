# Traffica Flow

## 1. Overview

The `Traffica Flow` handles SMS and VOICE data processing. It involves transferring data from the source to a staging area, processing it in HDFS and Hive, and ultimately storing it in Impala tables.

## 2. Installation & Configuration

### Scripts & Configuration
- Install dependencies
- Configure Oozie

## 3. Data Processing

### SMS

**Schedule**: `every 35 minutes`  
**Scheduler**: `Java Springboot Application`  
**User**: `traffica`  
**Active Node**: `unc2.bigdata.abc.gr`  
**Backup Node**: `unc1.bigdata.abc.gr`  
**Installation directory**: `/shared/abc/traffica`  
**Logs**: `/shared/abc/traffica/logs`  
**Configuration File**: `/shared/abc/traffica/config/application.yml`  
**Start command**:  
```bash
supervisorctl start traffica_sms
```
**Stop command**:  
```bash
supervisorctl stop traffica_sms
```
**Enable command (un-pause)**:  
```bash
curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/enable"
```

### VOICE

**Schedule**: `every 20 minutes`  
**Scheduler**: `Java Springboot Application`  
**User**: `traffica`  
**Active Node**: `unc2.bigdata.abc.gr`  
**Backup Node**: `unc1.bigdata.abc.gr`  
**Installation directory**: `/shared/abc/traffica`  
**Logs**: `/shared/abc/traffica/logs`  
**Configuration File**: `/shared/abc/traffica/config/application.yml`  
**Start command**:  
```bash
supervisorctl start traffica_voice
```
**Stop command**:  
```bash
supervisorctl stop traffica_voice
```
**Enable command (un-pause)**:  
```bash
curl -X PUT "http://unc2.bigdata.abc.gr:11482/traffica/app/operations/lifecycle/enable"
```

## 4. Monitoring & Debugging

### Logs
- Logs stored in `/shared/abc/traffica/logs`
- To check logs for errors:
```bash
grep -i -e error -e exception /shared/abc/traffica/logs/traffica-sms.log
zgrep -i -e error -e exception /shared/abc/traffica/logs/<yearMonthFolder>/<name_of_logfile>
```
- Check application status:
```bash
curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/info/health"
curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/info/check"
```
- UI with endpoints:  
  [Swagger UI](http://unc2.bigdata.abc.gr:11483/traffica/swagger-ui/index.html#/)

## 5. Troubleshooting

### Alerts

**Mail Subject:** `Traffica Application failed`  
Possible messages:
1. `Traffica sms main flow failed.`
2. `Traffica sms application has been paused due to multiple sequential failures. Manual actions are needed.`
3. `Traffica sms application has been paused due to inability to rename local files. Manual actions are needed.`
4. `Traffica sms application has been paused due to inability to clean up files. Manual actions are needed.`

### Troubleshooting Steps

- Check if the application is running:
```bash
curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/info/check"
```
- Check the logs for errors to identify the root cause:
```bash
# For the current log file
grep -i -e error -e exception /shared/abc/traffica/logs/traffica-sms.log

# For older compressed files
zgrep -i -e error -e exception /shared/abc/traffica/logs/<yearMonthFolder>/<name_of_logfile>
```
- Check metrics and error rates from Grafana:

  Open Firefox using VNC and go to  
  [Grafana Dashboard](https://unc1.bigdata.abc.gr:3000/d/qIM5rod4z/traffica)

  Use panels ending in `Err` to identify problematic components and steps.

  Use `Files`, `Size`, `Rows` to identify if input has changed.

- If there is a problem renaming files with the `.LOADED` suffix:

  From `unc2` as `traffica`:
  ```bash
  # Get files that were processed correctly
  grep 'filelist=' /shared/abc/traffica/logs/traffica-sms.log 

  # Move files pending rename from the list above
  cd /data/1/trafficaftp/Traffica_XDR
  mv <file>{,.LOADED}
  ```

- If the root cause is resolved, resume normal operation.

  The flow has been designed with auto-recovery. It marks only successfully loaded files as `.LOADED` and handles/cleans up all staging directories on each run.

  From `unc2` with personal user:
  ```bash
  # Check if scheduling is enabled 
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/disabled"

  # If the above command returns true
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/enable"
  ```

  - If `unc2` is down, then manually start the application on `unc1`. This requires that VIP `cne.def.gr` has been migrated and SFTP is working on `unc1`.

## 6. Data Validation & Checks

- Ensure `.LOADED` suffix is added to processed files.
- Validate the number of records in Impala:
```sql
SELECT COUNT(*) FROM sai.sms_raw;
SELECT COUNT(*) FROM sai.voice_raw;
```
- Confirm all partitions are loaded correctly.

## 7. Miscellaneous Notes

- Ndefs:

  From `unc2` with personal account:
  ```bash
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/info/health" # HTTP 200 if app is up
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/info/check" # returns message if up
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/shutdown/gracefully" # Shutdown application. If flow is running, then wait to finish. App should terminate ONLY with this method.
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/disable" # Disable flow scheduling
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/enable" # Enable flow scheduling
  curl -X GET "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/lifecycle/disabled" # True if disabled, else false
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/cleanup/all" # Run cleanup on demand
  curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/main/run" # Run flow on demand
  ```

- For further monitoring and debugging, access the UI with endpoints available from VNC:  
  [Traffica API Swagger](http://unc2.bigdata.abc.gr:11483/traffica/swagger-ui/index.html#/)

