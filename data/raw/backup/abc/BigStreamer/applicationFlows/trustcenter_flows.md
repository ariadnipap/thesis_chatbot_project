# TrustCenter Flows

## 1. Overview

TrustCenter Flows handle various data extraction and processing tasks related to Location Mobility, Router Analytics, Application Data Usage Insights, and Customer Satisfaction Index. These flows extract data from BigStreamer into files, which are then transferred to an exchange directory for TrustCenter to process.

## 2. Installation & Configuration

### Scripts & Configuration
- Install dependencies
- Configure Oozie

## 3. Data Processing

### Location Mobility

Location Mobility (LM) refers to extracting data from BigStreamer into files.  
The output files are transferred to an exchange directory so that a service, TrustCenter, reads and deletes them.

**File formats**:
- `LM_02_lte_yyyyMMdd_xxx.txt`
- `LM_03_smsIn_yyyyMMdd_xxx.txt`
- `LM_04_smsOut_yyyyMMdd_xxx.txt`
- `LM_05_voiceInOut_yyyyMMdd_xxx.txt`
- `LM_06_voiceIn_yyyyMMdd_xxx.txt`
- `LM_07_voiceOut_yyyyMMdd_xxx.txt`
- `LM_08_cellHist_yyyyMMdd_xxx.txt`

A reconciliation log is also created, storing execution timestamps, file names, and line counts.

### Router Analytics

Router Analytics (RA) extracts data from BigStreamer into files that are compressed and transferred to an exchange directory for TrustCenter.

**File formats**:
- `RA_01_yyyymmdd_00001_x.gz`
- `RA_02_yyyymmdd_00001_x.gz`
- `RA_03_yyyymmdd.gz`

### Application Data Usage Insights

Application Data Usage Insights (AUI) extracts data from BigStreamer into files that are compressed and transferred to an exchange directory for TrustCenter.

**File format**:
- `AUI_01_yyyymmdd_0000x.txt`

### Customer Satisfaction Index

Customer Satisfaction Index (CSI) extracts data from BigStreamer into files that are compressed and transferred to an exchange directory for TrustCenter.

**File formats**:
- `CSI_fix_mmddyyyy_wXX.txt`
- `CSI_mob_mmddyyyy_mmddyyyy.txt`

## 4. Monitoring & Debugging

### Logs
- Logs are stored in `/shared/abc/location_mobility/logging`
- Each flow has its own log files, typically named using the flow's identifier.

To check log files:
```bash
cat /shared/abc/location_mobility/logging/LM_05_voiceInOut_reconciliation.log
```

To check error messages:
```bash
grep -i -e error -e exception /shared/abc/location_mobility/log/*.log
```

To monitor real-time logs:
```bash
tail -f /shared/abc/location_mobility/log/lm_export_lte_v2_mon.cron.$(date '+%Y%m%d').log
```

## 5. Troubleshooting

### Location Mobility Issues
- If files are missing, check if they have been automatically exported in the reconciliation log.
- If data is missing, ensure `eea.eea_hour`, `sai.sms_raw_v`, `osix.osix_sms_raw`, or other relevant tables have been populated.
- If the script appears stuck, check for lock files in `/shared/abc/location_mobility/run/`.

To manually rerun an export script:
```bash
/shared/abc/location_mobility/run/renew/export_lm_lte_v2_mon.sh --max-files 6 >> /shared/abc/location_mobility/log/lm_export_lte_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
```

To rerun a script for a specific date:
```bash
/shared/abc/location_mobility/run/renew/export_lm_lte_v2_mon.sh -t 20220313 --max-files 6 >> /shared/abc/location_mobility/log/lm_export_lte_v2_mon.cron.$(date '+%Y%m%d').log 2>&1
```

### Router Analytics Issues
- If files are missing, verify if `npce.device_session` and `npce.device_traffic` tables contain the necessary data.
- If the script is stuck, check for lock files in `/shared/abc/location_mobility/run/`.

To manually rerun:
```bash
/shared/abc/location_mobility/run/export_ra_bs_01.sh --max-files 6 >> /shared/abc/location_mobility/log/ra_export_bs_01.oozie.`date +%Y%m%d`.log 2>&1
```

### Application Data Usage Insights Issues
- If logs show `date: invalid date ‘NULL 6 hours ago’`, it indicates missing data in `npce.abc_apps_raw_events`.

To manually rerun:
```bash
/shared/abc/location_mobility/run/export_aui.sh -t 20220313 >> /shared/abc/location_mobility/log/aui_export_bs_01.oozie.`date +%Y%m%d`.log 2>&1
```

### Customer Satisfaction Index Issues
- If logs indicate `Problem with 20220108.`, it means data is missing in `sai.cube_indicators_it` or `sai.sub_aggr_csi_it`.

To manually rerun:
```bash
/shared/abc/export_sai_csi/run/export_csi_fix.sh 20220313 >> /shared/abc/export_sai_csi/log/sai_csi.cron.`date +%Y%m%d`.log 2>&1
```

## 6. Data Validation & Checks

- Ensure that exported files exist in `/data/location_mobility/out/` and `/shared/abc/export_sai_csi/out/`.
- Check the number of records in Impala:
```sql
SELECT COUNT(*) FROM sai.sms_raw;
SELECT COUNT(*) FROM sai.voice_raw;
SELECT COUNT(*) FROM npce.device_session;
```
- Verify reconciliation logs for expected row counts.

## 7. Miscellaneous Notes

- If scripts are stuck, check for lock files:
```bash
ls /shared/abc/location_mobility/run/*.lock
```
- For manually triggering exports:
```bash
curl -X PUT "http://unc2.bigdata.abc.gr:11483/traffica/app/operations/main/run"
```
- UI with endpoints for debugging is available:
  [Swagger UI](http://unc2.bigdata.abc.gr:11483/traffica/swagger-ui/index.html#/)


