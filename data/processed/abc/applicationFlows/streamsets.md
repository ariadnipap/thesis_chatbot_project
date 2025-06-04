---
title: Streamsets Pipeline Operations
system: BigStreamer
component: Streamsets
tool: StreamSets Data Collector
location: un2.bigdata.abc.gr
user: sdc
monitoring: mysql.jobstatus
hdfs_paths:
  - /ez/landingzone/StreamSets/aums
  - /ez/landingzone/StreamSets/eems
  - /ez/landingzone/StreamSets/energy_efficiency
  - /ez/landingzone/StreamSets/nemo
  - /ez/landingzone/StreamSets/open_weather_map
log_path: /shared/sdc/log/sdc.log
streamsets_ui: https://un2.bigdata.abc.gr:18636
hue_ui: https://un-vip.bigdata.abc.gr:8888
retention_policy: varies_by_pipeline
schedule: varies_by_pipeline
description: |
  Streamsets flows automate ingestion of CSV/ZIP files from SFTP sources,
  transform the data, and load it into Hive and Impala tables partitioned by date.
  Each pipeline corresponds to a data feed from a remote system such as AUMS, EEMS, Energy Efficiency, Nemo, or OpenWeatherMap.
  - streamsets
  - hdfs ingestion
  - data pipeline
  - aums
  - eems
  - nemo
  - energy efficiency
  - sftp to hive
  - sdc
  - data engineering
  - troubleshooting
  - monitoring
---
# Streamsets
**Utility Node / Server:** `un2.bigdata.abc.gr`  
**User:** `sdc`  
**[Password](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/devpasswd.kdbx)**   
**Logs:** `/shared/sdc/log/sdc.log`  
**Log Retention:** `10 days`  
**Configuration:** `/shared/sdc/configuration/pipelines.properties`  
**Streamsets:** `https://un2.bigdata.abc.gr:18636`  
**Hue:** `https://un-vip.bigdata.abc.gr:8888`
## Streamsets Flows
Streamsets pipelines automate the ingestion of remote SFTP data files into Hive/Impala. Each flow handles decompression, transformation, and loading based on naming conventions and partitioned timestamps.
`Streamsets Flows` are used for getting files from sftp remdef resources, processing them, storing them into HDFS directories and loading the file data into Hive and Impala tables. The tables are partitioned based on the file name which contain a timestamp (e.g. \*\_20181121123916.csv -> par_dt='20181121'). 
``` mermaid
  graph TD
    C[Remdef Sftp Server]
    A[SFTP] --> |Transform and Place Files|B[HDFS]
    B --> |Transform and Run Query|D[Hive]
    style C fill:#5d6d7e
```
### AUMS
| Pipelines | Status |
| --------- | ------ |
| AUMS Data File Feed | Running |
| AUMS Metadata File Feed | Running |
#### AUMS Data File Feed
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`   
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/aums/`  
**SFTP Compressed File:** `aems_data_*.zip` containing `data_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/aums/archive_data` 
**Hive Database:** `aums`  
**Hive Table Name:** `archive_data`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `AUMS Data File Feed`
#### AUMS Metadata File Feed
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`    
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/aums/`  
**SFTP Compressed File:** `aems_data_*.zip` containing `metadata_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/aums/archive_metadata` 
**Hive Database:** `aums`  
**Hive Table Name:** `archive_metadata`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `AUMS Metadata File Feed`
### EEMS
| Pipelines | Status |
| --------- | ------ |
| EEMS Data File Feed | Running |
| EEMS Metadata File Feed | Running |
#### EEMS Data File Feed
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`   
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/aums_eems/`  
**SFTP Compressed File:** `aems_data_*.zip` containing `data_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/aums/eems_archive_data/` 
**Hive Database:** `aums`  
**Hive Table Name:** `eems_archive_data`  
**Hive Retention:** `2 years`
**Logs `grep` keyword**: `EEMS Data File Feed`
#### EEMS Metadata File Feed
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/aums_eems/`  
**SFTP Compressed File:** `aems_data_*.zip` containing `metadata_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/aums/eems_archive_metadata/` 
**Hive Database:** `aums`  
**Hive Table Name:** `eems_archive_metadata`  
**Hive Retention:** `2 years`
**Logs `grep` keyword**: `EEMS Metadata File Feed`
### Energy-Efficiency
| Pipelines | Status |
| --------- | ------ |
| energy_efficiency enodeb_auxpiu | Running |
| energy_efficiency enode_boards | Running |
| energy_efficiency enodeb_vswr | Running |
| energy_efficiency nodeb_auxpiu | Running |
| energy_efficiency nodeb_boards | Running |
| energy_efficiency nodeb_vswr | Running |
| energy_efficiency tcu_temperatures | Running | 
| energy_efficiency cells | Running |
| energy_efficiency Huawei_potp_sdh_hour | _Stopped_ |
| energy_efficiency Huawei_potp_wdm_hour | _Stopped_ |
| energy_efficiency baseband FAN TEST | Running |
| energy_efficiency baseband RET TEST | Running |
| energy_efficiency baseband SFP TEST | Running |
| energy_efficiency baseband TEMP SERIAL TEST | Running |
| energy_efficiency baseband VSWR TEST | Running |
| energy_efficiency basebandsouth FAN TEST | Running |
| energy_efficiency basebandsouth RET TEST | Running |
| energy_efficiency basebandsouth SFP TEST | Running |
| energy_efficiency basebandsouth TEMP SERIAL TEST | Running |
| energy_efficiency basebandsouth VSWR TEST | Running |
#### Energy Efficiency enodeb_auxpiu
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `eNodeB_AuxPIU_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/enodeb_auxpiu/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `enodeb_auxpiu`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency enodeb_auxpiu`
#### Energy Efficiency enode_boards
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `eNodeB_boards_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/enodeb_board/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `enodeb_board`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency enode_boards`
#### Energy Efficiency enodeb_vswr
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `eNodeB_VSWR_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/enodeb_vswr` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `enodeb_vswr`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency enodeb_vswr`
#### Energy Efficiency nodeb_auxpiu
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `NodeB_AuxPIU_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/nodeb_auxpiu/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `nodeb_auxpiu`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency enodeb_auxpiu`
#### Energy Efficiency nodeb_boards
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `NodeB_boards_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/nodeb_board/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `nodeb_board`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency enode_boards`
#### Energy Efficiency nodeb_vswr
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `NodeB_VSWR_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/nodeb_vswr/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `nodeb_vswr`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency nodeb_vswr`
#### Energy Efficiency tcu_temperatures
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `TCU_tempratures_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/tcu_temperatures/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `tcu_temperatures`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency tcu_temperatures`
#### Energy Efficiency cells
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `NodeB_Cells_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/cell/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `cell`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency cells`
#### Energy Efficiency Huawei_potp_sdh_hour
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `none`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/huawei_potp_sdh_hour/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `huawei_potp_sdh_hour`  
**Hive Retention:** `none`
#### Energy Efficiency Huawei_potp_wdm_hour
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `none`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/huawei_potp_wdm_hour/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `huawei_potp_wdm_hour`  
**Hive Retention:** `none`
#### Energy Efficiency baseband FAN TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `baseband_FAN_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandnorth_fan/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandnorth_fan`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency baseband FAN TEST`
#### Energy Efficiency baseband RET TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `baseband_RET_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandnorth_ret/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandnorth_ret`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency baseband RET TEST`
#### Energy Efficiency baseband SFP TEST 
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `baseband_SFP_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandnorth_sfp/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandnorth_sfp`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency baseband SFP TEST`
#### Energy Efficiency baseband TEMP SERIAL TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `baseband_TEMP_SERIAL_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandnorth_temp_serial/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandnorth_temp_serial`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency basebandsouth TEMP SERIAL TEST`
#### Energy Efficiency baseband VSWR TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `baseband_VSWR_*.csv`
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandnorth_vswr/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandnorth_vswr`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency basebandsouth VSWR TEST`
#### Energy Efficiency basebandsouth FAN TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `basebandsouth_FAN_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandsouth_fan/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandsouth_fan`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency basebandsouth FAN TEST`
#### Energy Efficiency basebandsouth RET TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `basebandsouth_RET_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandsouth_ret/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandsouth_ret`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency baseband RET TEST`
#### Energy Efficiency basebandsouth SFP TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `basebandsouth_SFP_*.csv`
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandsouth_sfp/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandsouth_sfp`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency basebandsouth SFP TEST`
#### Energy Efficiency basebandsouth TEMP SERIAL TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `basebandsouth_TEMP_SERIAL_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/basebandsouth_temp_serial/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandsouth_temp_serial`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency baseband TEMP SERIAL TEST`
#### Energy Efficiency basebandsouth VSWR TEST
**SFTP User:** `bigd`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/ossrc/`  
**SFTP File:** `basebandsouth_VSWR_*.csv`  
**HDFS Path:** `/ez/landingzone/StreamSets/energy_efficiency/' basebandsouth_vswr'/` 
**Hive Database:** `energy_efficiency`  
**Hive Table Name:** `basebandsouth_vswr`  
**Hive Retention:** `none`
**Logs `grep` keyword**: `energy_efficiency basebandsouth VSWR TEST`
### Nemo
| Pipelines | Status |
| --------- | ------ |
| Nemo Network Connectivity | Running |
| Nemo Video | _Stopped_ |
| Nemo Voice | Running |
| Nemo Signal Coverage | Running |
| Nemo Datahttp | Running |
| Nemo Web | _Stopped_ |
| Nemo Data Session v2 | Running | 
| Nemo Streaming Session | Running |
| Nemo Call Session | Running |
#### Nemo Network Connectivity
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/`  
**SFTP Compressed File:** `netcon__1_*.gz`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/network_connectivity_details_investigation/`
**Hive Database:** `nemo`  
**Hive Table Name:** `network_connectivity_details_investigation`  
**Hive Retention:** `60 partitions`
**Logs `grep` keyword**: `Nemo Network Connectivity`
#### Nemo Video
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/`  
**SFTP Compressed File:** `video__1_*.gz`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/video_details_investigation/`
**Hive Database:** `nemo`  
**Hive Table Name:** `video_details_investigation`  
**Hive Retention:** `60 partitions`
#### Nemo Voice
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/`  
**SFTP Compressed File:** `voice__1_*.gz`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/voice_details_investigation/`
**Hive Database:** `nemo`  
**Hive Table Name:** `voice_details_investigation`  
**Hive Retention:** `60 partitions`
**Logs `grep` keyword**: `Nemo Voice`
#### Nemo Signal Coverage
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/`  
**SFTP Compressed File:** `cov__1_*.gz`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/signal_coverage_details_investigation/`
**Hive Database:** `nemo`  
**Hive Table Name:** `signal_coverage_details_investigation`  
**Hive Retention:** `60 partitions`
**Logs `grep` keyword**: `Nemo Signal Coverage`
#### Nemo Datahttp
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/`  
**SFTP Compressed File:** `datahttp__1_*.gz`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/datahttp_details_investigation/`
**Hive Database:** `nemo`  
**Hive Table Name:** `datahttp_details_investigation`  
**Hive Retention:** `60 partitions`
**Logs `grep` keyword**: `Nemo Datahttp`
#### Nemo Web
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/`  
**SFTP Compressed File:** `web__1_*.gz`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/web_details_investigation/`
**Hive Database:** `nemo`  
**Hive Table Name:** `web_details_investigation`  
**Hive Retention:** `60 partitions`
#### Nemo Data Session v2
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/Handy_Files/`  
**SFTP File:** `DATA_*.csv`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/data_session/`
**Hive Database:** `nemo`  
**Hive Table Name:** `data_session`  
**Hive Retention:** `60 partitions`
**Logs `grep` keyword**: `Nemo Data Session v2`
#### Nemo Streaming Session
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/Handy_Files/`  
**SFTP File:** `STREAMING_*.csv`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/streaming_session/`
**Hive Database:** `nemo`  
**Hive Table Name:** `streaming_session`  
**Hive Retention:** `60 partitions`
**Logs `grep` keyword**: `Nemo Streaming Session`
#### Nemo Call Session
**SFTP User:** `nbi`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/data/ftp/sftp/uploads/Handy_Files/`  
**SFTP File:** `CALL_*.csv`
**HDFS Path:** `/ez/landingzone/StreamSets/nemo/call_session/`
**Hive Database:** `nemo`  
**Hive Table Name:** `call_session`  
**Hive Retention:** `60 partitions`
**Logs `grep` keyword**: `Nemo Call Session`
### Open Weather Map
| Pipelines | Status |
| --------- | ------ |
| open_weather_map_pipeline | Running |
#### Open weather map pipelin
**SFTP User:** `ipvpn`  
**SFTP Password:** `passwordless`  
**SFTP Server:** `999.999.999.999`  
**SFTP Path:** `/shared/vantage_ref-data/REF-DATA/OpenWeatherMap/`  
**SFTP File:** `OpenWeatherMap_*`
**HDFS Paths:**
- `/ez/landingzone/StreamSets/open_weather_map/openweathermap_final/{pardt}/{weather}`  
- `/ez/landingzone/StreamSets/open_weather_map/openweathermap_forecast/{pardt}/{weather}`
**Hive Database:** `open_weather_map`  
**Hive Table Names:**
- `openweathermap_forecast`  
- `openweathermap_final`    
**Hive Retention:** `none`
**Logs `grep` keyword**: `open_weather_map_pipeline`
## Monitoring
Monitoring is done via a MySQL jobstatus database, and pipeline status is also tracked in Streamsets UI. Only successful loads are recorded; failed executions generate alerts via email.
_Connection Details_
**Database Type:** `mysql`   
**Host:** `db-vip.bigdata.abc.gr:3306`  
**DB Name:** `monitoring`  
**DB User:** `monitoring`  
**DB Password:** `https://metis.ghi.com/obss/bigdata/abc/devops/devops-projects/-/blob/master/System_Users/abc_dev.kdbx`  
**Table:** `jobstatus`  
**Connection command:** `/usr/bin/mysql -u monitoring -p -h db-vip.bigdata.abc.gr:3306 monitoring`
_General details_
**Requests:**
- **Add:** Monitoring `add http requests` for **only** `SUCCESS` status. (FAILED status is not handled)
- **Email:** If the pipeline `fails` to execute at any stage, an email alert is sent through the Streamsets UI.  
**operativePartition:** is created from the filename `*_YYYYMMDD\*.csv`
### EEMS
#### EEMS Data File Feed
##### Components
| Component | Status | Description |
| ------ | ------ | ------ |
| SFTP_HDFS | SUCCESS | Sftp get the raw files from the remdef server, process them and put the parsing files into HDFS landingzone |
| MAIN | SUCCESS | Indicates the status of the whole load |
For `FAILED` components an `email` is sent through `Streamsets UI`.
##### Records
For each execution the following set of messages will be recorded in the Monitoring database.
| id | execution_id | application | job | component | operative_partition | status | system_ts | 
| ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| 813749 | 7db009eb-e2b7-4379-8c00-393ac732b66e | EEMS | EEMS_DATA_FILE_FEED | SFTP_HDFS | 20230104 | SUCCESS | 2023-01-05T01:20:23.000Z |
| 813750 | 7db009eb-e2b7-4379-8c00-393ac732b66e | EEMS | EEMS_DATA_FILE_FEED | MAIN | 20230104 | SUCCESS | 2023-01-05T01:20:28.000Z |
##### Database Queries
###### MySQL: List details of the last load
```
select 
execution_id, id, application, job, component, operative_partition,  
status, system_ts, system_ts_end, message   
from jobstatus a where upper(job) like 'EEMS_DATA_FILE_FEED%'   
and execution_id=(select max(execution_id) from jobstatus where upper(job) like 'EEMS_DATA_FILE_FEED%');
```
###### Application: List details of specific load
```
curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=EEMS&job=EEMS_DATA_FILE_FEED&component=SFTP_HDFS&operativePartition=20230104'
```
#### EEMS Metadata File Feed
##### Components
| Component | Status | Description |
| ------ | ------ | ------ |
| SFTP_HDFS | SUCCESS | Sftp get the raw files from the remdef server, process them and put the parsing files into HDFS landingzone |
| MAIN | SUCCESS | Indicates the status of the whole load |
For `FAILED` components an `email` is sent through `Streamsets UI`.
##### Records
For each pipeline execution the following set of messages will be recorded in the Monitoring database.
| id | execution_id | application | job | component | operative_partition | status | system_ts | 
| ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| 808931 | 7bfb8fda-1573-46d0-be7f-a9f297538042 | EEMS | EEMS_METADATA_FILE_FEED | SFTP_HDFS | 20230104 | SUCCESS | 2023-01-04T17:28:03.000Z |
| 808932 | 7bfb8fda-1573-46d0-be7f-a9f297538042 | EEMS | EEMS_METADATA_FILE_FEED | MAIN | 20230104 | SUCCESS | 2023-01-04T17:28:07.000Z |
##### Database Queries
###### MySQL: List details of the last load
```
select 
execution_id, id, application, job, component, operative_partition,  
status, system_ts, system_ts_end, message   
from jobstatus a where upper(job) like 'EEMS_METADATA_FILE_FEED%'   
and execution_id=(select max(execution_id) from jobstatus where upper(job) like 'EEMS_METADATA_FILE_FEED%');
```
###### Application: List details of specific load
```
curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=EEMS&job=EEMS_METADATA_FILE_FEED&component=SFTP_HDFS&operativePartition=20230104'
```
## Troubleshooting
If a pipeline fails, this section provides step-by-step instructions to diagnose the issue using Streamsets UI, system logs, and Hive partition checks.
Following troubleshooting steps apply to all pipelines.
**Step 1:** Log in to [Stremsets](https://un2.bigdata.abc.gr:18636/) with `sdc` user.
1. Check that the specific pipeline has the status `RUNNING`. If it has any other status continue the investigation.   
1. Open a pipeline. Check the generic summary (click anywhere in the board and select summary) to get an overview through dashboards on the data processed and errors. Also check if any job of the pipeline has errors (click on an action box and select tab Errors). Streamset will provide a specific ERROR message.
**Step 2:** Look at the `logs`.
**TO VIEW THE LOG FILE FOR A SPECIFIC PIPELINE:** `cat sdc.log | grep -i '<pipeline-grep-keyword>'`
1. Through the `Stramsets UI`, `logs` can be viewed by pressing the paper icon (second) on the top right corner of the selected pipeline environment.
1. Open `logs` and apply some filters in order to retrieve the information related to the specific pipeline. Logs can be found at `/shared/sdc/log/sdc.log`. To search logs use `grep` or open log file with `less sdc.log` and search `'/'`.
    1. Grep for `Started reading file` to see when a new file is parsed successfully:
        ```
        cat sdc.log | grep -i 'Started reading file'
        ```
        > 2022-03-22 14:00:03,419 [user:\*sdc] [pipeline:energy_efficiency basebandsouth RET TEST/energyeffd112ecef-f20d-45ff-bef4-b88f2117e3d7] [runner:] [thread:ProductionPipelineRunnable-energyeffd112ecef-f20d-45ff-bef4-b88f2117e3d7-energy_efficiency basebandsouth RET TEST] INFO  RemdefDownloadSource - **Started reading file**: /`basebandsouth_RET_20220322-092713.csv`
    1. Grep `Error while attempting to parse file` for error while parsing files:
        ```
        cat sdc.log | grep -i 'Error while attempting to parse file'
        ```
        > ERROR RemdefDownloadSource - **Error while attempting to parse file**: /`baseband_TEMP_SERIAL_20220322-081534.csv`
        > java.io.IOException: (line 3331) invalid char between encapsulated token and delimiter
    1. Grep `A JVM error occurred while running the pipeline` for JVM errors:
        ```
        cat sdc.log | grep -i 'A JVM error occurred while running the pipeline'
        ```
        > ERROR ProductionPipelineRunnable - A JVM error occurred while running the pipeline, java.lang.OutOfMemoryError: Java heap     space java.lang.OutOfMemoryError: Java heap space
    1. Grep `ERROR` for any errors that might occur.
    1. Following `WARN` message with exceptions does not affect the insertion of data:
        ```
        2022-03-31 00:20:14,058 [user:*sdc] [pipeline:AUMS Metadata File Feed/AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2] [runner:0] [thread:ProductionPipelineRunnable-AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2-AUMS Metadata File Feed] WARN  UserGroupInformation - PriviledgedActionException as:sdc/un2.bigdata.abc.gr@CNE.abc.GR (auth:KERBEROS) cause:java.sql.SQLException: org.apache.thrift.transport.TTransportException: java.net.SocketException: Broken pipe (Write failed)
        2022-03-31 00:20:14,058 [user:*sdc] [pipeline:AUMS Metadata File Feed/AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2] [runner:0] [thread:ProductionPipelineRunnable-AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2-AUMS Metadata File Feed] INFO  HiveConfigBean - Connection to Hive become stale, reconnecting.
        2022-03-31 00:20:14,058 [user:*sdc] [pipeline:AUMS Metadata File Feed/AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2] [runner:0] [thread:ProductionPipelineRunnable-AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2-AUMS Metadata File Feed] WARN  TIOStreamTransport - Error closing output stream.
        java.net.SocketException: Socket is closed
        ......
        2022-03-31 00:20:14,059 [user:*sdc] [pipeline:AUMS Metadata File Feed/AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2] [runner:0] [thread:ProductionPipelineRunnable-AUMSMetadf3f82d52-871f-4df9-b9e1-c5e8180971c2-AUMS Metadata File Feed] INFO  HiveConfigBean - Error closing stale connection Error while cleaning up the server resources
        java.sql.SQLException: Error while cleaning up the server resources
        ......
        Caused by: org.apache.thrift.transport.TTransportException: javax.net.ssl.SSLException: Connection has been shutdown: javax.net.ssl.SSLException: java.net.SocketException: Broken pipe (Write failed)
        ......
        Caused by: javax.net.ssl.SSLException: Connection has been shutdown: javax.net.ssl.SSLException: java.net.SocketException: Broken pipe (Write failed)
        ......
        Caused by: javax.net.ssl.SSLException: java.net.SocketException: Broken pipe (Write failed)
        ......
        Caused by: java.net.SocketException: Broken pipe (Write failed)
        ......
        ```
**Step 3:** Log in to [Hue](https://un-vip.bigdata.abc.gr:8888/hue/editor/?type=impala) with `intra` user, and check the status of loaded partitions of the tables which correspond to the pipeline.
1. Run query `show partitions <database>.<table>`. 
1. If the table has no partitions or no stats you can use following query to check the partitions under investigation:  
`select count(*), par_dt from <database>.<table> where par_dt > '<partition>' group by par_dt order by par_dt desc;`
  - Ndef: Execute `REFRESH <table_name>` if Hive and Impala tables have different data.
**Step 4:** Check if there are files in sftp remdef directory, which haven't been processed and loaded into hive and impala tables. This is accomplished through comparing the file in the remdef directory and the partitions found in the hdfs directory.
1. Access and view SFTP files in remdef directory
    1. Login to `un2` and change to `sdc` user. 
    1. From there execute `sftp <sftp-user>@<sftp-server>:<sftp-path>`.
    1. Run `ls -ltr` to view the latest files in the remdef directory.
    1. Check that the files have the correct credential permissions and rights, `sftp user` and at least `-rw-r-----` permission. 
1. Access and view partitions in hdfs directory
    1. Login to `un2` and change to `sdc` user.
    1. From there execute `hdfs dfs -ls <hdfs-path>`.
    1. Make sure partitions are created in the correct hdfs path.
Finally, check for each file if there is an equivalent partition created. The partition's format is `YYYYMMDD` and it derives from the file name.
**Step 5:** If the errors has been resolved and the pipeline status is (`EDITED` or `STOPPED`), start the pipeline and wait to see if the errors have been indeed fixed and no other errors have occurred due to the latest changes.
---
---
### Common Problems and Ways to Fix them
There are some issues that occur quite often while using `Streamsets` flows. If any of the issues mentioned below happen, firstly follow the general troubleshooting steps to identify the problem that occurred and then follow the steps which correspond to fixing the issue. 
---
#### Check file(s) has been loaded correctly
Login to `un2.bigdata.abc.gr` and change to `sdc` user. 
**Step 1:** Execute `sftp <sftp-user>@<sftp-server>:<sftp-path>`, run `ls -ltr` to view the latest files in the remdef directory and check that the files have the correct credential permissions and rights. The user must be the `sftp user` and permissions be at least `-rw-r----- `.
Example:
```
-rw-r-----    1 nbi      nbi         87987 Jan  4 11:57 STREAMING_W52_2022.csv
-rw-r-----    1 nbi      nbi       1795960 Jan  4 11:57 DATA_SESSIONS_W52_2022.csv
-rw-r-----    1 nbi      nbi        284724 Dec 22 11:56 CALL_SESSIONS_W50_2022.csv
```
**Step 2:** Get the file(s) with "YYYYMMDD-HHMMss" as the datetime of the file you want to check its integrity from the sftp remdef directory by running `get <filaname> <local-path>`. The file will be copied in `un2` at the location `<local-path>`. A usefull local path is `/tmp/streamsets`. If does not exist just create it `mkdir /tmp/streamsets`
**Step 3:** Execute `wc -l <filename>` to count the number of lines the file has.
**Step 4:** Compare the number of lines with the equivalent value of records in the corresponding partition by running (in [Hue](https://999.999.999.999:8888/hue/editor/?type=impala) or with secimp) 
```
select count(*), par_dt from <database>.<table> where par_dt='<partition>' group by par_dt;
```
Command `refresh tables` might be needed.
**Step 5:** If the `returned result of records of the impala query` is equal to the `returned result of 'wc -l \*\_YYYYMMDD-HHMMss.csv' -1`, then the flow was executed correctly for the csv file for the examined date.
**Step 6:** Clear the local directory from the unnecessary fetched data.
---
#### Manually inserting missing data in Hive and Impala
---
To manually insert missing data in Hive and Impala there are two ways.
A. Manually get and put the files with the missing data from the Streamsets pipeline remdef directory **(Suggested Way)**
  For each file:
  1. From `un2.bigdata.abc.gr` with user `sdc` execute `sftp <sftp-user>@<sftp-server>:<sftp-path>`.
  1. From the sftp remdef directory, fetch locally the missing data by running `get <filename>.csv/zip <local-path>`. The file will be copied in `un2.bigdata.abc.gr` at `<local-path>`. A usefull local path is `/tmp/streamsets`. If does not exist just create it `mkdir /tmp/streamsets`
  1. From the sftp remdef directory, put the recently fetched data in the directory again with a different name by executing `put <local-path>/<filename>.csv/zip <filename>_tmp.csv/zip`. This will result with the new file having a different name and timestamp (last modified) so the pipeline can see it and process it. 
  1. When the Streamset pipeline has finished processing the data, remove the `<filename>_tmp.csv/zip` file from the remdef sftp directory with the sftp command `rm <filename>_tmp.csv/zip`. `!IMPORTANT`
  1. Clear the local directory from the unnecessary fetched data.
B. Configure the offset of the Streamset
  1. Select the wanted pipeline and `Stop` it
  1. Select from the top right toolbar of the pipeline the `...` option and press `Reset Origin`
  1. Select the component `SFTP FTP Client 1`
  1. Go to Configuration panel and select the `SFTP/FTP/FTPS` and take the value found in the `File Name Pattern` field
  1. Change the property `File Name Pattern` with the exact file name you want the stream to start processing. This sets the `offset` to the name of the file you set in the above field.
  1. `Wait` for the file to be processed
  1. `Stop` the pipeline again
  1. `Reset` the `File Name Pattern` to its previous value
  1. `Start` the pipeline  
  This will make the Streamset pipeline to process only the specific files. For more information about offset and origin press [here](https://metis.ghi.com/obss/bigdata/documentation/-/wikis/dev/frameworks/streamsets#offset-through-streamset-gui).
---
#### Manually correct faulty data in Hive and Impala
---
**Step 1:** Check the faulty partitions by following the procedure found [here](#check-files-has-been-loaded-correctly).
**Step 2:** In `Hue` as `intra`, delete existing wrong partitions that overlap with the required interval from kudu table and/or from impala table. 
  - If it is in kudu (10 most recent days are in kudu), do: `ALTER table <database>.<table> DROP IF EXISTS RANGE PARTITION 'v1'<= values < 'v2';`, where v1 and v2 the range of partitions. 
  - If it is in impala, do: `ALTER table <database>.<table> DROP IF EXISTS PARTITION (par_dt='v1');`, where v1 the wanted partition.
**Step 3:** Follow the instruction [here](#manually-inserting-data-missing-in-hive-and-impala) to load the recently deleted data.
### Exceptions and Possible Root Causes
1.  `CONTAINER_0001 - net.schmizz.sshj.connection.ConnectionException: Stream closed`  
    - SFTP Server side issue which results to missing data.
1. `CONTAINER_0001 - net.schmizz.sshj.sftp.SFTPException: Permission denied`  
    - Files are put in sftp directory with wrong user and file permissions and later changed to the correct ones
    - Password and user were changed at the SFTP server but not updated in streamsets
    - SFTP Server side issue
1. `A JVM error occurred while running the pipeline, java.lang.OutOfMemoryError: Java heap space`
    - SFTP Server read file issue. Logs will have "Broken transport; encoutered EOF" errors. This could happen as a result of issues with SFTP Server which causes Java heap space errors.
1. `TTransportException: java.net.SocketException: Connection closed by remdef host`
```
2023-01-12 11:50:21,208 [user:*sdc] [pipeline:EEMS Data File Feed/EEMSData7adbe2c9-4c70-425b-a475-fc766cd02ada] [runner:0] [thread:ProductionPipelineRunnable-EEMSData7adbe2c9-4c70-425b-a475-fc766cd02ada-EEMS Data File Feed] INFO  HiveConfigBean - Error closing stale connection Error while cleaning up the server resources
java.sql.SQLException: Error while cleaning up the server resources
...
Caused by: org.apache.thrift.transport.TTransportException: java.net.SocketException: Connection closed by remdef host
2023-01-15 15:00:09,403 [user:sdc] [pipeline:energy_efficiency baseband VSWR TEST/energyeffa1e8ea2e-6e09-4529-889e-740157783fd8] [runner:0] [thread:ProductionPipelineRunnable-energyeffa1e8ea2e-6e09-4529-889e-740157783fd8-energy_efficienc
y baseband VSWR TEST] WARN  UserGroupInformation - PriviledgedActionException as:sdc/un2.bigdata.abc.gr@CNE.abc.GR (auth:KERBEROS) cause:java.sql.SQLException: [Simba][ImpalaJDBCDriver](500593) Communication link failure. Failed
to connect to server. Reason: java.net.SocketException: Broken pipe (Write failed).
2023-01-15 15:00:09,403 [user:sdc] [pipeline:energy_efficiency baseband VSWR TEST/energyeffa1e8ea2e-6e09-4529-889e-740157783fd8] [runner:0] [thread:ProductionPipelineRunnable-energyeffa1e8ea2e-6e09-4529-889e-740157783fd8-energy_efficienc
y baseband VSWR TEST] INFO  HiveConfigBean - Connection to Hive become stale, reconnecting.
2023-01-15 15:00:09,408 [user:sdc] [pipeline:energy_efficiency baseband VSWR TEST/energyeffa1e8ea2e-6e09-4529-889e-740157783fd8] [runner:0] [thread:ProductionPipelineRunnable-energyeffa1e8ea2e-6e09-4529-889e-740157783fd8-energy_efficienc
y baseband VSWR TEST] INFO  HiveConfigBean - Error closing stale connection [Simba][JDBC](10060) Connection has been closed.
java.sql.SQLNonTransientConnectionException: [Simba][JDBC](10060) Connection has been closed.
```