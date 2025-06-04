---
title: TrustCenter Data Export Flows
description: Overview and support guide for TrustCenter-related export workflows including Location Mobility, Router Analytics, Application Usage Insights (AUI), and Customer Satisfaction Index (CSI). Describes scheduling, file formats, SFTP transfers, Impala sources, Oozie jobs, and troubleshooting procedures.
author: mtuser / intra / ABC BigStreamer Team
updated: 2025-05-01
tags:
  - trustcenter
  - location mobility
  - lm
  - router analytics
  - ra
  - application usage insights
  - aui
  - customer satisfaction index
  - csi
  - oozie
  - sftp
  - export flows
  - bigstreamer
  - impala
  - reconciliation logs
---
# TrustCenter Flows
This is a document that will assist on support. Business documents can be found [here](https://metis.ghi.com/obss/bigdata/abc/reporting/reporting/-/tree/master/mini%20projects/location_mobility/docs).
## Location Mobility
Location Mobility (LM) reffers to extraction of data from BigStreamer into files.  
The output files are transferred to an exchange directory so that a service, TrustCenter which is managed by def, reads and deletes them.  
These files are:
- `LM_02_lte_yyyyMMdd_xxx.txt`
- `LM_03_smsIn_yyyyMMdd_xxx.txt`
- `LM_04_smsOut_yyyyMMdd_xxx.txt`
- `LM_05_voiceInOut_yyyyMMdd_xxx.txt`
- `LM_06_voiceIn_yyyyMMdd_xxx.txt`
- `LM_07_voiceOut_yyyyMMdd_xxx.txt`
- `LM_08_cellHist_yyyyMMdd_xxx.txt`
Along with those, the reconciliation files are produced and sent for each one.  
They give information on the date of the execution, the name of the file, the export date and the number of lines it contains.
``` bash
cat /shared/abc/location_mobility/logging/LM_05_voiceInOut_reconciliation.log
#e.g for LM_05_voiceInOut and 1st of February 2022
2022-02-01 08:06:33 LM_05_voiceInOut_20220201_00001.txt 20220201 20906
2022-02-01 10:02:36 LM_05_voiceInOut_20220201_00002.txt 20220201 23810
2022-02-01 12:02:45 LM_05_voiceInOut_20220201_00003.txt 20220201 179719
2022-02-01 14:03:45 LM_05_voiceInOut_20220201_00004.txt 20220201 876051
2022-02-01 16:05:13 LM_05_voiceInOut_20220201_00005.txt 20220201 1581201
2022-02-01 20:02:00 LM_05_voiceInOut_20220201_00006.txt 20220201 1606966
```
**Reconcilication Files**:  
`/shared/abc/location_mobility/logging/LM_*` on `un2.bigdata.abc.gr`
**Troubleshooting Steps**:
- Check to see if the file was produced at the right time and contained the expected number of rows.
### LM_02_lte
Under normal circumstances this file is produced every 2 hours and contains data for 2 hours from the Impala table `eea.eea_hour`.  
The filename format is `LM_02_lte_yyyyMMdd_xxx.txt` where `xxx` is a serial number between `01` and `12`.  
For example, if the file contains data for the 1st of March 2022 from 02:00 to 04:00 the filename will be `LM_02_lte_20220301_00002.txt`.
``` mermaid
  graph TD
  A[Oozie Coord: Location_Mobility_2Hour_CO] -->|SHELL| B[Master Script ]
  B --> C[ Remdef Script ]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `mtuser`
**Scheduler**: `Oozie`
**Schedule**: `Every 2 hours`  
**Coordinator**: `Location_Mobility_2Hour_CO`
**Master Script**: `000.Location_Mobility_Hourly_Oozie_Main.sh`
**Remdef Script**: `mtuser@un2:/shared/abc/location_mobility/run/run_lm_exports_hourly.sh`
The master script triggers the export procedure.
``` mermaid
  graph TD 
  A[Impala: eea.eea_hour] -->| Impala Query | B1[location_mobility.lm_lte_exp]
  B1 --> |Merge HDFS files to a single file | B2[File: LM_02_lte_yyyyMMdd_000xx.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B2 --> |SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /lm]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/lm`
**Logs**: ```/shared/abc/location_mobility/log/lm_export_lte_v2_mon.cron.$(date '+%Y%m%d').log```
**Script**: `/shared/abc/location_mobility/run/renew/export_lm_lte_v2_mon.sh` on `un2.bigdata.abc.gr`
**SQL Script**: `/shared/abc/location_mobility/run/renew/export_lm_lte_v2_mon.sh` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/eea_hour.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:  
	- login on `un2.bigdata.abc.gr` with personal account  
	- `su - mtuser`
    ``` logs
    # e.g for 2021-02-22
    [...] - INFO: end_date=2021-02-22 09:00:00
    [...] - INFO: max_date=2021-02-22 09:00:00
    ```
    If end_date is newer or equal to max_date, it means that table `eea.eea_hour` does not contain new data and therefore there is nothing to be done during this execution.  
		abc should load data in `eea.eea_hour` table first and then execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more files weren't exported execute the script with the `--max-files <N>` flag.  
This will instruct the script to catch-up meaning to export files for N 2-hour intervals.  
This is not needed if 4 or less files were missed in which case the procedure will automatically catch up.  
For example if 6 files were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_lte_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/lm_export_lte_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
- If you need to export files for a specific date execute the script with the `-t <yyyymmdd>` flag. For example if the first 6 files for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_lte_v2_mon.sh -t 20220313 --max-files 6 >> /shared/abc/location_mobility/log/lm_export_lte_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
### LM_03_smsIn
Under normal circumstances this file is produced every 2 hours and contains data for 2 hours from the Impala tables `sai.sms_raw_v, osix.osix_sms_raw` that fulfill some conditions.  
The filename format is `LM_03_smsIn_yyyyMMdd_xxx.txt` where `xxx` is a serial number between `01` and `12`.  
For example, if the file contains data for the 1st of March 2022 from 02:00 to 04:00 the filename will be `LM_03_smsIn_20220301_00002.txt`.
``` mermaid
  graph TD
  A[Oozie Coord: Location_Mobility_2Hour_CO] -->|SHELL| B[Master Script ]
  B --> C[ Remdef Script ]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `mtuser`
**Scheduler**: `Oozie`
**Schedule**: `Every 2 hours`  
**Coordinator**: `Location_Mobility_2Hour_CO`
**Master Script**: `000.Location_Mobility_Hourly_Oozie_Main.sh`
**Remdef Script**: `mtuser@un2:/shared/abc/location_mobility/run/run_lm_exports_hourly.sh`
The master script triggers the export procedure.
``` mermaid
graph TD
  A[Impala: sai.sms_raw_v] --> |union all | D[Impala: osix.osix_sms_raw ] --> | Impala Query | B[File: LM_03_smsIn_yyyyMMdd_xxx.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /lm]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/lm`
**Logs**: ```/shared/abc/location_mobility/log/lm_export_sms_in_v2_mon.cron.$(date '+%Y%m%d').log```
**Script**: `/shared/abc/location_mobility/run/renew/export_lm_sms_in_v2_mon.sh` on `un2.bigdata.abc.gr`
**SQL Script**: `/shared/abc/location_mobility/run/renew/export_lm_sms_in_v2.sql` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/sms_in.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Check if this message exists in the failed execution's log:  
	- login on `un2.bigdata.abc.gr` with personal account  
	- `su - mtuser`
    ``` logs
    [...] - INFO: Nothing to export.
    ```
    This means that tables `sai.sms_raw_v` or `osix.osix_sms_raw` do not contain new data and therefore there is nothing to be done during this execution.  
    New data should be loaded in the following tables and then execute the script.  
		- `sai.sms_raw`, updated by TRAFFICA flow (`sai.sms_raw_v` is a view on `sai.sms_raw` table).  
		- `osix.osix_sms_raw`, responsible abc
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_lm_sms_in_v2_mon.sh` return no process means the previous execution was forcefully stopped. Delete the lock file `/shared/abc/location_mobility/run/sms_in.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more files weren't exported execute the script with the `--max-files <N>` flag.  
This will instruct the script to catch-up meaning to export files for N 2-hour intervals.  
This is not needed if 4 or less files were missed in which case the procedure will automatically catch up.  
For example if 6 files were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_sms_in_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/lm_export_sms_in_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
- If you need to export files for a specific date execute the script with the `-t <yyyymmdd>` flag.  
For example if the first 6 files for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_sms_in_v2_mon.sh -t 20220313 --max-files 6 >> /shared/abc/location_mobility/log/lm_export_sms_in_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
### LM_04_smsOut
Under normal circumstances this file is produced every 2 hours and contains data for 2 hours from the Impala tables `sai.sms_raw_v, osix.osix_sms_raw` that fulfill some conditions.  
The filename format is `LM_04_smsOut_yyyyMMdd_xxx.txt` where `xx` is a serial number between `01` and `12`.  
For example, if the file contains data for the 1st of March 2022 from 02:00 to 04:00 the filename will be `LM_04_smsOut_20220301_00002.txt`.
``` mermaid
  graph TD
  A[Oozie Coord: Location_Mobility_2Hour_CO] -->|SHELL| B[Master Script ]
  B --> C[ Remdef Script ]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `mtuser`
**Scheduler**: `Oozie`
**Schedule**: `Every 2 hours`  
**Coordinator**: `Location_Mobility_2Hour_CO`
**Master Script**: `000.Location_Mobility_Hourly_Oozie_Main.sh`
**Remdef Script**: `mtuser@un2:/shared/abc/location_mobility/run/run_lm_exports_hourly.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: sai.sms_raw_v] --> |union all | D[Impala: osix.osix_sms_raw ] -->| Impala Query | B[File: LM_04_smsOut_yyyyMMdd_xxx.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /lm]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/lm`
**Logs**: ```/shared/abc/location_mobility/log/lm_export_sms_out_v2_mon.cron.$(date '+%Y%m%d').log```
**Script**: `/shared/abc/location_mobility/run/renew/export_lm_sms_out_v2_mon.sh` on `un2.bigdata.abc.gr`
**SQL Script**: `/shared/abc/location_mobility/run/renew/export_lm_sms_out_v2.sql` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/sms_out.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Check if this message exists in the failed execution's log:  
	- login on `un2.bigdata.abc.gr` with personal account  
	- `su - mtuser`
    ``` logs
    [...] - INFO: Nothing to export.
    ```
    This means that table `sai.sms_raw_v` or `osix.osix_sms_raw` do not contain new data and therefore there is nothing to be done during this execution.  
    New data should be loaded in the following tables and then execute the script.  
		- `sai.sms_raw`, updated by TRAFFICA flow (`sai.sms_raw_v` is a view on `sai.sms_raw` table).  
		- `osix.osix_sms_raw`, responsible abc
- If failed execution's log contains the message
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_lm_sms_out_v2_mon.sh` return no process means the previous execution was forcefully stopped.  
		Delete the lock file `/shared/abc/location_mobility/run/sms_out.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more files weren't exported execute the script with the `--max-files <N>` flag.  
This will instruct the script to catch-up meaning to export files for N 2-hour intervals.  
This is not needed if 4 or less files were missed in which case the procedure will automatically catch up.  
For example if 6 files were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_sms_out_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/lm_export_sms_out_v2_mon.cron.$(date '+%Y%m%d') 2>&1
    ```
- If you need to export files for a specific date execute the script with the `-t <yyyymmdd>` flag. For example if the first 6 files for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_sms_out_v2_mon.sh -t 20220313 --max-files 6 >> /shared/abc/location_mobility/log/lm_export_sms_out_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
### LM_05_voiceInOut
Under normal circumstances this file is produced every 2 hours and contains data for 2 hours from the Impala tables `sai.voice_raw_v, osix.osix_voice_raw` that fulfill some conditions. 
The filename format is `LM_05_voiceInOut_yyyyMMdd_xxx.txt` where `xxx` is a serial number between `01` and `12`.  
For example, if the file contains data for the 1st of March 2022 from 02:00 to 04:00 the filename will be `LM_05_voiceInOut_20220301_00002.txt`.
``` mermaid
  graph TD
  A[Oozie Coord: Location_Mobility_2Hour_CO] -->|SHELL| B[Master Script ]
  B --> C[ Remdef Script ]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `mtuser`
**Scheduler**: `Oozie`
**Schedule**: `Every 2 hours`  
**Coordinator**: `Location_Mobility_2Hour_CO`
**Master Script**: `000.Location_Mobility_Hourly_Oozie_Main.sh`
**Remdef Script**: `mtuser@un2:/shared/abc/location_mobility/run/run_lm_exports_hourly.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: sai.voice_raw_v] --> |union all | D[Impala: osix.osix_voice_raw ] --> | Impala Query | B[File: LM_05_voiceInOut_yyyyMMdd_xxx.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /lm]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/lm`
**Logs**: ```/shared/abc/location_mobility/log/lm_export_voice_inout_v2_mon.cron.$(date '+%Y%m%d').log```
**Script**: `/shared/abc/location_mobility/run/renew/export_lm_voice_inout_v2_mon.sh` on `un2.bigdata.abc.gr`
**SQL Script**: `/shared/abc/location_mobility/run/renew/export_lm_voice_inout_v2.sql` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/voice_inout.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Check if this message exists in the failed execution's log:  
	- login on `un2.bigdata.abc.gr` with personal account  
	- `su - mtuser`
    ``` logs
    [...] - INFO: Nothing to export.
    ```
    This means that table `sai.voice_raw_v` or `osix.osix_voice_raw` do not contain new data and therefore there is nothing to be done during this execution.
    New data should be loaded in the following tables and then execute the script.  
		- `sai.voice_raw`, updated by TRAFFICA flow (`sai.voice_raw_v` is a view on `sai.voice_raw` table).  
		- `osix.osix_voice_raw`, responsible abc
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_lm_voice_inout_v2_mon.sh` return no process means the previous execution was forcefully stopped.  
		Delete the lock file `/shared/abc/location_mobility/run/voice_inout.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more files weren't exported execute the script with the `--max-files <N>` flag.  
This will instruct the script to catch-up meaning to export files for N 2-hour intervals.  
This is not needed if 4 or less files were missed in which case the procedure will automatically catch up.  
For example if 6 files were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_voice_inout_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/lm_export_voice_inout_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
- If you need to export files for a specific date execute the script with the `-t <yyyymmdd>` flag. For example if the first 6 files for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_voice_inout_v2_mon.sh -t 20220313 --max-files 6 >> /shared/abc/location_mobility/log/lm_export_voice_inout_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
### LM_06_voiceIn
Under normal circumstances this file is produced every 2 hours and contains data for 2 hours from the Impala tables `sai.voice_raw_v, osix.osix_voice_raw` that fulfill some conditions.  
The filename format is `LM_06_voiceIn_yyyyMMdd_xxx.txt` where `xxx` is a serial number between `01` and `12`.  
For example, if the file contains data for the 1st of March 2022 from 02:00 to 04:00 the filename will be `LM_06_voiceIn_20220301_00002.txt`.
``` mermaid
  graph TD
  A[Oozie Coord: Location_Mobility_2Hour_CO] -->|SHELL| B[Master Script ]
  B --> C[ Remdef Script ]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `mtuser`
**Scheduler**: `Oozie`
**Schedule**: `Every 2 hours`  
**Coordinator**: `Location_Mobility_2Hour_CO`
**Master Script**: `000.Location_Mobility_Hourly_Oozie_Main.sh`
**Remdef Script**: `mtuser@un2:/shared/abc/location_mobility/run/run_lm_exports_hourly.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: sai.voice_raw_v] --> |union all | D[Impala: osix.osix_voice_raw ] -->| Impala Query | B[File: LM_06_voiceIn_yyyyMMdd_xxx.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /lm]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/lm`
**Logs**: ```/shared/abc/location_mobility/log/lm_export_voice_in_v2_mon.cron.$(date '+%Y%m%d').log```
**Script**: `/shared/abc/location_mobility/run/renew/export_lm_voice_in_v2_mon.sh` on `un2.bigdata.abc.gr`
**SQL Script**: `/shared/abc/location_mobility/run/renew/export_lm_voice_in_v2.sql` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/voice_in.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Check if this message exists in the failed execution's log:  
	- login on `un2.bigdata.abc.gr` with personal account  
	- `su - mtuser`
    ``` logs
    [...] - INFO: Nothing to export.
    ```
    This means that table `sai.voice_raw_v` or `osix.osix_voice_raw` do not contain new data and therefore there is nothing to be done during this execution. 
    New data should be loaded in the following tables and then execute the script.  
		- `sai.voice_raw`, updated by TRAFFICA flow (`sai.voice_raw_v` is a view on `sai.voice_raw` table).  
		- `osix.osix_voice_raw`, responsible abc
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_lm_voice_in.sh` return no process means the previous execution was forcefully stopped. Delete the lock file `/shared/abc/location_mobility/run/voice_in.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more files weren't exported execute the script with the `--max-files <N>` flag.  
This will instruct the script to catch-up meaning to export files for N 2-hour intervals.  
This is not needed if 4 or less files were missed in which case the procedure will automatically catch up. For example if 6 files were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_voice_in_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/lm_export_voice_in_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
- If you need to export files for a specific date execute the script with the `-t <yyyymmdd>` flag. For example if the first 6 files for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_voice_in_v2_mon.sh -t 20220313 --max-files 6 >> /shared/abc/location_mobility/log/lm_export_voice_in_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
### LM_07_voiceOut
Under normal circumstances this file is produced every 2 hours and contains data for 2 hours from the Impala tables `sai.voice_raw_v, osix.osix_voice_raw` that fulfill some conditions.  
The filename format is `LM_07_voiceOut_yyyyMMdd_xxx.txt` where `xxx` is a serial number between `01` and `12`.  
For example, if the file contains data for the 1st of March 2022 from 02:00 to 04:00 the filename will be `LM_07_voiceOut_20220301_00002.txt`.
``` mermaid
  graph TD
  A[Oozie Coord: Location_Mobility_2Hour_CO] -->|SHELL| B[Master Script ]
  B --> C[ Remdef Script ]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `mtuser`
**Scheduler**: `Oozie`
**Schedule**: `Every 2 hours`  
**Coordinator**: `Location_Mobility_2Hour_CO`
**Master Script**: `000.Location_Mobility_Hourly_Oozie_Main.sh`
**Remdef Script**: `mtuser@un2:/shared/abc/location_mobility/run/run_lm_exports_hourly.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: sai.voice_raw_v] --> |union all | D[Impala: osix.osix_voice_raw ] -->| Impala Query | B[File: LM_07_voiceOut_yyyyMMdd_xxx.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /lm]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/lm`
**Logs**: ```/shared/abc/location_mobility/log/lm_export_voice_out_v2_mon.cron.$(date '+%Y%m%d').log```
**Script**: `/shared/abc/location_mobility/run/renew/export_lm_voice_out_v2_mon.sh` on `un2.bigdata.abc.gr`
**SQL Script**: `/shared/abc/location_mobility/run/renew/export_lm_voice_out_v2.sql` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/voice_out.lock`
**Troubleshooting Steps**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- Identify system or service errors in the log file e.g failed Impala query.
- Check if this message exists in the failed execution's log:  
	- login on `un2.bigdata.abc.gr` with personal account  
	- `su - mtuser`
    ``` logs
    [...] - INFO: Nothing to export.
    ```
    This means that table `sai.voice_raw_v` or `osix.osix_voice_raw` do not contain new data and therefore there is nothing to be done during this execution. 
    New data should be loaded in the following tables and then execute the script.  
		- `sai.voice_raw`, updated by TRAFFICA flow (`sai.voice_raw_v` is a view on `sai.voice_raw` table).  
		- `osix.osix_voice_raw`, responsible abc
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_lm_voice_out_v2_mon.sh` return no process means the previous execution was forcefully stopped. Delete the lock file `/shared/abc/location_mobility/run/voice_out.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more files weren't exported execute the script with the `--max-files <N>` flag. This will instruct the script to catch-up meaning to export files for N 2-hour intervals. This is not needed if 4 or less files were missed in which case the procedure will automatically catch up. For example if 6 files were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_voice_out_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/lm_export_voice_out_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
- If you need to export files for a specific date execute the script with the `-t <yyyymmdd>` flag. For example if the first 6 files for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_voice_out_v2_mon.sh -t 20220313 --max-files 6 >> /shared/abc/location_mobility/log/lm_export_voice_out_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
    ```
### LM_08_cellHist
Under normal circumstances this file is produced every day and contains yesterday's data from the Impala table `refdata.rd_cells_v`.  
The filename format is `LM_08_cellHist_yyyyMMdd_00001.txt`.  
For example, if the file contains data for the 1st of March 2022 the filename will be `LM_08_cellHist_20220301_00001.txt`.
``` mermaid
  graph TD
  A[Oozie Coord: Location_Mobility_Daily_CO] -->|SHELL| B[Master Script ]
  B --> C[ Remdef Script ]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `mtuser`
**Scheduler**: `Oozie`
**Schedule**: `Every day at 07:00`  
**Coordinator**: `Location_Mobility_Daily_CO`
**Master Script**: `000.Location_Mobility_Daily_Oozie_Main.sh`
**Remdef Script**: `mtuser@un2:/shared/abc/location_mobility/run/run_lm_exports_daily.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: refdata.rd_cells_v] -->| Impala Query | B[File: LM_08_cellHist_yyyyMMdd_00001.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /lm]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/lm`
**Logs**: ```/shared/abc/location_mobility/log/export_lm_rd_cells_v2_mon.oozie.$(date '+%Y%m%d').log```
**Script**: `/shared/abc/location_mobility/run/renew/export_lm_rd_cells_v2_mon.sh` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/rd_cells.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:  
	- login on `un2.bigdata.abc.gr` with personal account  
	- `su - mtuser`
    ``` logs
    [...] - INFO: max_date=yyyyMMdd and export_date=yyyyMMdd
    ```
    If the desired export_date is newer than max_date, it means that table `refdata.rd_cells_v` does not contain new data and therefore there is nothing to be done during this execution.  
		Load table `refdata.rd_cells` first and then execute the script.
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_lm_rd_cells.sh` return no process means the previous execution was forcefully stopped. Delete the lock file `/shared/abc/location_mobility/run/rd_cells.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded.  
Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more dates weren't exported execute the script with the `--max-files <N>` flag.  
This will instruct the script to catch-up meaning to export files for N dates.  
This is not needed if 4 or less dates were missed in which case the procedure will automatically catch up.  
For example if 6 dates were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_rd_cells_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/export_lm_rd_cells_v2_mon.oozie.$(date '+%Y%m%d').log 2>&1
    ```
- If you need to export file for a specific date execute the script with the `-t <yyyymmdd>` flag. For example if file for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/renew/export_lm_rd_cells_v2_mon.sh -t 20220313 >> /shared/abc/location_mobility/log/export_lm_rd_cells_v2_mon.oozie.$(date '+%Y%m%d').log 2>&1
    ```
## Router Analytics
Router Analytics (RA) reffers to extraction of data from BigStreamer into files. The output files are compressed and transferred to an exchange directory so that a service, TrustCenter which is managed by def, reads and deletes them. These files are:
- `RA_01_yyyymmdd_00001_x.gz` 
- `RA_02_yyyymmdd_00001_x.gz`
- `RA_03_yyyymmdd.gz`
Along with those, the reconciliation files are produced and sent for each one. They give information on the date of the execution, the name of the file, the export date and the number of lines it contains.
``` bash
cat /shared/abc/location_mobility/logging/RA_BS_01_reconciliation.log
#e.g for LM_05_voiceInOut and 31st of January 2022
2022-02-01 09:06:39 RA_01_20220131_00001_[0-5] 20220131 68579162
```
**Reconcilication Files**: `/shared/abc/location_mobility/logging/RA_BS_*` on `un2.bigdata.abc.gr`
**Troubleshooting Steps**:
- Check to see if the file was produced at the right time and contained the expected number of rows.
### RA_01
Under normal circumstances this file is produced every day and contains yesterday's data from the Impala table `npce.device_session`. The filename format is `RA_01_yyyymmdd_00001_x.gz` where `x` is a serial number between `1` and `5` as due to size the file is split into subfiles. For example, the files containing data for the 1st of March 2022 will be `RA_01_20220301_00001_[0-5].gz`.
``` mermaid
  graph TD
  A[Oozie: export_Router_Analytics_files_daily] -->|SSH| B[Host: un2.bigdata.abc.gr <br> User: intra2]
  B -->|sudo to mtuser| C[Master Script]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `intra`
**Scheduler**: `Oozie`
**Schedule**: `Every day at 07:00`  
**Coordinator**: `export_Router_Analytics_files_daily`
**Master Script**: `/shared/abc/location_mobility/run/run_ra_exports.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: npce.device_session] -->| Impala Query | B[File: RA_01_yyyymmdd_00001_x.gz <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /ra]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/ra`
**Logs**: ```/shared/abc/location_mobility/log/ra_export_bs_01.oozie.`date +%Y%m%d`.log```
**Script**: `/shared/abc/location_mobility/run/export_ra_bs_01.sh` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/ra_01.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:
    ``` logs
    # e.g for 2021-02-01
    [...] - INFO: max_date=20220131 and export_date=20220131
    ```
    If the desired export_date is newer than max_date, it means that table `npce.device_session` does not contain new data and therefore there is nothing to be done during this execution. Communicate with def to load the table first and then execute the script.
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_ra_bs_01.sh` return no process means the previous execution was forcefully stopped. Delete the lock file `/shared/abc/location_mobility/run/ra_01.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded. Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 4 or more dates weren't exported execute the script with the `--max-files <N>` flag. This will instruct the script to catch-up meaning to export files for N dates. This is not needed if 3 or less dates were missed in which case the procedure will automatically catch up. **Make sure there is sufficient space both in the local path and the sftp path**. For example if 5 dates were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_ra_bs_01.sh --max-files 6 >> /shared/abc/location_mobility/log/ra_export_bs_01.oozie.`date +%Y%m%d`.log 2>&1
    ```
- If you need to export file for a specific date execute the script with the `-t <yyyymmdd>` flag. **Make sure there is sufficient space both in the local path and the sftp path**. For example if file for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_ra_bs_01.sh -t 20220313 >> /shared/abc/location_mobility/log/ra_export_bs_01.oozie.`date +%Y%m%d`.log 2>&1
    ```
### RA_02
Under normal circumstances this file is produced every day and contains yesterday's data from the Impala table `npce.device_traffic`. The filename format is `RA_02_yyyymmdd_00001_x.gz` where `x` is a serial number between `1` and `5` as due to size the file is split into subfiles. For example, the files containing data for the 1st of March 2022 will be `RA_02_20220301_00001_[0-5].gz`.
``` mermaid
  graph TD
  A[Oozie: export_Router_Analytics_files_daily] -->|SSH| B[Host: un2.bigdata.abc.gr <br> User: intra2]
  B -->|sudo to mtuser| C[Master Script]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `intra`
**Scheduler**: `Oozie`
**Schedule**: `Every day at 07:00`  
**Coordinator**: `export_Router_Analytics_files_daily`
**Master Script**: `/shared/abc/location_mobility/run/run_ra_exports.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: npce.device_traffic] -->| Impala Query | B[File: RA_02_yyyymmdd_00001_x.gz <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /ra]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/ra`
**Logs**: ```/shared/abc/location_mobility/log/ra_export_bs_02.oozie.`date +%Y%m%d`.log```
**Script**: `/shared/abc/location_mobility/run/export_ra_bs_02.sh` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/ra_02.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:
    ``` logs
    # e.g for 2021-02-01
    [...] - INFO: max_date=20220131 and export_date=20220131
    ```
    If the desired export_date is newer than max_date, it means that table `npce.device_traffic` does not contain new data and therefore there is nothing to be done during this execution. Communicate with def to load the table first and then execute the script.
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_ra_bs_02.sh` return no process means the previous execution was forcefully stopped. Delete the lock file `/shared/abc/location_mobility/run/ra_02.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded. Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 4 or more dates weren't exported execute the script with the `--max-files <N>` flag. This will instruct the script to catch-up meaning to export files for N dates. This is not needed if 3 or less dates were missed in which case the procedure will automatically catch up. **Make sure there is sufficient space both in the local path and the sftp path**. For example if 5 dates were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_ra_bs_02.sh --max-files 6 >> /shared/abc/location_mobility/log/ra_export_bs_02.oozie.`date +%Y%m%d`.log 2>&1
    ```
- If you need to export file for a specific date execute the script with the `-t <yyyymmdd>` flag. **Make sure there is sufficient space both in the local path and the sftp path**. For example if file for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_ra_bs_02.sh -t 20220313 >> /shared/abc/location_mobility/log/ra_export_bs_02.oozie.`date +%Y%m%d`.log 2>&1
    ```
### RA_03
Under normal circumstances this file is produced every Wednesday and contains past week's data from the Impala table `npce.device_dms`. The filename format is `RA_03_yyyymmdd.gz`. For example, the files containing data up to the 2nd of March 2022 will be `RA_03_20220302.gz`.
``` mermaid
  graph TD
  A[Oozie: export_Router_Analytics_files_daily] -->|SSH| B[Host: un2.bigdata.abc.gr <br> User: intra2]
  B -->|sudo to mtuser| C[Master Script]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `intra`
**Scheduler**: `Oozie`
**Schedule**: `Every Wednesday at 16:00`  
**Coordinator**: `export_Router_Analytics_files_to_mediation_ra_03_weekly`
**Master Script**: `/shared/abc/location_mobility/run/run_ra_03_export.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: npce.device_dms] -->| Impala Query | B[File: RA_03_yyyymmdd.gz <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /ra]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/ra`
**Logs**: ```/shared/abc/location_mobility/log/ra_export_bs_03.oozie.`date +%Y%m%d`.log```
**Script**: `/shared/abc/location_mobility/run/export_ra_bs_03.sh` on `un2.bigdata.abc.gr`
**Lock file**: `/shared/abc/location_mobility/run/ra_03.lock`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:
    ``` logs
    # e.g for 2021-01-26
    [...] - INFO: max_date=20220126 and export_date=20220202
    ```
    If the desired export_date is newer than max_date, it means that table `npce.device_dms` does not contain new data and therefore there is nothing to be done during this execution. Communicate with def to load the table first and then execute the script.
- If failed execution's log contains the message:
    ``` logs
    [...] - ERROR: Script is being executed by another process. Exiting..
    ```
    and `ps -ef | grep export_ra_bs_03.sh` return no process means the previous execution was forcefully stopped. Delete the lock file `/shared/abc/location_mobility/run/ra_03.lock` and execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded. Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 2 or more files weren't exported execute the script with the `--max-files <N>` flag. This will instruct the script to catch-up meaning to export files for N executions. **Make sure there is sufficient space both in the local path and the sftp path**. For example if 2 files were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_ra_bs_03.sh --max-files 2 >> /shared/abc/location_mobility/log/ra_export_bs_03.oozie.`date +%Y%m%d`.log 2>&1
    ```
- If you need to export file for a specific date execute the script with the `-t <yyyymmdd>` flag. **Make sure there is sufficient space both in the local path and the sftp path**. For example if file for 16th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_ra_bs_03.sh -t 20220316 >> /shared/abc/location_mobility/log/ra_export_bs_03.oozie.`date +%Y%m%d`.log 2>&1
    ```
## Application Data Usage Insights
Application Data Usage Insights (AUI) reffers to extraction of data from BigStreamer into files. The output files are compressed and transferred to an exchange directory so that a service, TrustCenter which is managed by def, reads and deletes them. These files are:
- `AUI_01_yyyymmdd_0000x.txt`
Along with those, a reconciliation file are produced and sent. They give information on the date of the execution, the name of the file, the export date and the number of lines it contains.
``` bash
cat /shared/abc/location_mobility/logging/AUI_BS_01_reconciliation.log
#e.g for AUI_01 and 21st of February 2022
2021-02-22 06:00:09 AUI_01_20210221_00005.txt 20210221 15
```
**Reconcilication File**: `/shared/abc/location_mobility/logging/AUI_BS_01_reconciliation.log` on `un2.bigdata.abc.gr`
**Troubleshooting Steps**:
- Check to see if the file was produced at the right time and contained the expected number of rows.
### AUI_01
Under normal circumstances this file is produced every 4 hours and contains data from 6 to 2 hours ago of the Impala table `npce.abc_apps_raw_events`. The filename format is `AUI_01_yyyymmdd_0000x.txt` where `x` is a serial number between `1` and `6`. For example, the files containing data for the 1st of March 2022 from 00:00 to 04:00 will be `AUI_01_20220301_00001.txt`.
``` mermaid
  graph TD
  A[Oozie: export_Application_Data_Usage_Insights_files_4_hours] -->|SSH| B[Host: un2.bigdata.abc.gr <br> User: intra2]
  B -->|sudo to mtuser| C[Master Script]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `intra`
**Scheduler**: `Oozie`
**Schedule**: `Every 4 hours`  
**Coordinator**: `export_Application_Data_Usage_Insights_files_4_hours`
**Master Script**: `/shared/abc/location_mobility/run/run_aui_exports.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: npce.abc_apps_raw_events] -->| Impala Query | B[File: AUI_01_yyyymmdd_0000x.txt <br> Server: un2.bigdata.abc.gr <br> Path: /data/location_mobility/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /aui]
```
**User**: `mtuser`
**Local path**: `/data/location_mobility/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/aui`
**Logs**: ```/shared/abc/location_mobility/log/aui_export_bs_01.oozie.`date +%Y%m%d`.log```
**Script**: `/shared/abc/location_mobility/run/export_aui.sh` on `un2.bigdata.abc.gr`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:
    ``` logs
    date: invalid date ‘NULL 6 hours ago’
    ```
    This means that table `npce.abc_apps_raw_events` does not contain new data and therefore there is nothing to be done during this execution. Communicate with def to load the table first and then execute the script.
**Ndefs**:
- If files were missing the script will catch up at the next execution, assuming the table has been loaded. Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If 5 or more files weren't exported execute the script with the `--max-files <N>` flag. This will instruct the script to catch-up meaning to export files for N 4-hour intervals. This is not needed if 4 or less dates were missed in which case the procedure will automatically catch up. For example if 6 dates were not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_aui.sh --max-files 6 >> /shared/abc/location_mobility/log/aui_export_bs_01.oozie.`date +%Y%m%d`.log 2>&1
    ```
- If you need to export file for a specific date execute the script with the `-t <yyyymmdd>` flag. For example if file for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/location_mobility/run/export_aui.sh -t 20220313 >> /shared/abc/location_mobility/log/aui_export_bs_01.oozie.`date +%Y%m%d`.log 2>&1
    ```
## Customer Satisfaction Index
Customer Satisfaction Index (CSI) reffers to extraction of data from BigStreamer into files. The output files are compressed and transferred to an exchange directory so that a service, TrustCenter which is managed by def, reads and deletes them. These files are:
- `CSI_fix_mmddyyyy_wXX.txt`
- `CSI_mob_mmddyyyy_mmddyyyy.txt`
Along with those, a reconciliation file are produced and sent. They give information on the date of the execution, the name of the file, the export date and the number of lines it contains.
``` bash
cat /shared/abc/export_sai_csi/logging/CSI_mob_reconciliation.log
#e.g for CSI_mob and 30th of January 2022
2022-01-30 09:02:42  CSI_mob_01242022_01302022.txt  20220124  4223904
```
**Reconcilication File**: `/shared/abc/export_sai_csi/logging/CSI_*` on `un2.bigdata.abc.gr`
**Troubleshooting Steps**:
- Check to see if the file was produced at the right time and contained the expected number of rows.
### CSI_fix
Under normal circumstances this file is produced every 4 hours and contains data from 2 days ago ago of the Impala table `sai.cube_indicators_it`. The filename format is `CSI_fix_mmddyyyy_wXX.txt` where `XX` is a serial number between `1` and `52` for the week of the year. For example, the file containing data for the 2nd of February 2022 which belongs to the 5th week of the year, will be `CSI_fix_02042022_w05.txt`.
``` mermaid
  graph TD
  A[Oozie: export_CSI_fix_and_mobile_daily] -->|SSH| B[Host: un2.bigdata.abc.gr <br> User: intra2]
  B -->|sudo to mtuser| C[Master Script]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `intra`
**Scheduler**: `Oozie`
**Schedule**: `Every day at 7:00`  
**Coordinator**: `export_CSI_fix_and_mobile_daily`
**Master Script**: `/shared/abc/location_mobility/run/run_csi_exports_daily.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: sai.cube_indicators_it] -->| Impala Query | B[File: CSI_fix_mmddyyyy_wXX.txt <br> Server: un2.bigdata.abc.gr <br> Path: /shared/abc/export_sai_csi/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /csi]
```
**User**: `mtuser`
**Local path**: `/shared/abc/export_sai_csi/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/csi`
**Logs**: ```/shared/abc/export_sai_csi/log/sai_csi.cron.`date +%Y%m%d`.log```
**Script**: `/shared/abc/export_sai_csi/run/export_csi_fix.sh` on `un2.bigdata.abc.gr`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:
    ``` logs
    # e.g for 2022-01-10
    Problem with 20220108.
    ```
    This means that table `sai.cube_indicators_it` does not contain new data and therefore there is nothing to be done during this execution. Load table `brond.cube_indicators` first and then execute the script.
**Ndefs**:
- If one date was missing the script will catch up at the next execution, assuming the table has been loaded. Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If you need to export file for a specific date execute the script with argument `<yyyymmdd>` flag. For example if file for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/export_sai_csi/run/export_csi_fix.sh 20220313 >> /shared/abc/export_sai_csi/log/sai_csi.cron.`date +%Y%m%d`.log 2>&1
    ```
### CSI_mob
Under normal circumstances this file is produced every day and contains data for the current week of the Impala table `sai.sub_aggr_csi_it`. The filename format is `CSI_mob_mmddyyyy_mmddyyyy.txt` where the first date is the last loaded Monday and the second the current date. For example, the file containing data for the 2nd of February 2022 will be `CSI_mob_01312022_02022022.txt`.
``` mermaid
  graph TD
  A[Oozie: export_CSI_fix_and_mobile_daily] -->|SSH| B[Host: un2.bigdata.abc.gr <br> User: intra2]
  B -->|sudo to mtuser| C[Master Script]
```
The workflow triggers a master script which in turn executes the substeps
**User**: `intra`
**Scheduler**: `Oozie`
**Schedule**: `Every day at 7:00`  
**Coordinator**: `export_CSI_fix_and_mobile_daily`
**Master Script**: `/shared/abc/location_mobility/run/run_csi_exports_daily.sh`
The master script triggers the export procedure.
``` mermaid
graph TD 
  A[Impala: sai.sub_aggr_csi_it] -->| Impala Query | B[File: CSI_mob_mmddyyyy_mmddyyyy.txt <br> Server: un2.bigdata.abc.gr <br> Path: /shared/abc/export_sai_csi/out]
  B -->|SFTP| C[User: trustcenterftp <br> Server: cne.def.gr <br> SFTP Path: /csi]
```
**User**: `mtuser`
**Local path**: `/shared/abc/export_sai_csi/out`
**SFTP user**: `trustcenterftp`
**SFTP path**: `/csi`
**Logs**: ```/shared/abc/export_sai_csi/log/sai_csi.cron.`date +%Y%m%d`.log```
**Script**: `/shared/abc/export_sai_csi/run/export_csi_mob_daily.sh` on `un2.bigdata.abc.gr`
**Troubleshooting Steps**:
- Identify system or service errors in the log file e.g failed Impala query.
- Find in the failed execution's log the message:
    ``` logs
    # e.g for 2022-01-10
    Problem with 20220108.
    ```
    This means that table `sai.sub_aggr_csi_it` does not contain new data and therefore there is nothing to be done during this execution. Load table `sai.sub_aggr_csi_it` first and then execute the script.
**Ndefs**:
- If one date was missing the script will catch up at the next execution, assuming the table has been loaded. Before manually executing the script in this case, check if the missing file has been automatically exported in the reconciliation log.
- If you need to export file for a specific date execute the script with argument `<yyyymmdd>` flag. For example if file for 13th of March 2022 was not exported run:
    ``` bash
    /shared/abc/export_sai_csi/run/export_csi_mob_daily.sh 20220313 >> /shared/abc/export_sai_csi/log/sai_csi.cron.`date +%Y%m%d`.log 2>&1
    ```