# Syzefxis Flows

## 1. Overview

## 2. Installation & Configuration
### Useful Links
- [Business Documents](https://metis.ghi.com/obss/bigdata/abc/sizefxis/bigstreamer-sizefxis-devops/-/tree/master/docs)
- [MoP documents](https://metis.ghi.com/obss/bigdata/abc/sizefxis/bigstreamer-sizefxis-devops/-/tree/master/MOPs)
- Users **keePass file**: [abc-devpasswd.kdbx](../../../abc-devpasswd.kdbx)  
- **Troubleshooting Steps**: Refer to MoPs files in [devops repository](https://metis.ghi.com/obss/bigdata/abc/sizefxis/bigstreamer-sizefxis-devops/-/blob/master/MOPs/README.md?ref_type=heads) of the project

### Scripts & Configuration
- Install dependencies
- Configure Oozie

## 3. Data Processing

### Input Performance Data

#### Service Level Agreement (SLA) Metrics

##### Creation of raw files
- **Server**: `nnmprd01.abc.gr` (backup: `nnmdis01.abc.gr`)
- **User**: `custompoller`
- **Password**: `Passwordless SSH from intra@un2.bigdata.abc.gr`
- **Scheduler**: `Cron`
- **Schedule**: `Every 5 minutes`
- **Path**: `/home/custompoller/out`
- **Elements Configuration**: `/home/custompoller/conf/syzeyksis_syze1.config`
- **Logs**: `/home/custompoller/log/syzeyksis-$(date +%Y%m%d).log`
- **Script**: `/home/custompoller/run/run_syzeyksis_standby.sh`
- **Alerts**: Not monitored

##### Transfer to BigStreamer nodes
- **Server**: `un2.bigdata.abc.gr`
- **User**: `intra`
- **Scheduler**: `Cron`
- **Schedule**: `Every 10 minutes`
- **SFTP Server**:  `nnmprd01.abc.gr` (backup: `nnmdis01.abc.gr`)
- **SFTP Path**:  `./out`
- **SFTP User**: `custompoller`
- **SFTP Password**: `Passwordless Authentication with SSH Key`
- **Local Staging Path**: `/data/1/nnm_custompoller_LZ/archives`
- **HDFS Destination Path**: `/ez/landingzone/nnm_custompoller/raw/YYYYMMDDhhmm`
- **Logs**: `/shared/abc/nnm_custompoller/log/nnmcustompoller_cron.YYYYMMDD.log`
- **Configuration**: `/shared/abc/nnm_custompoller/DataParser/scripts/transferlist/nnm_custompoller.trn`
- **Script**:  `/shared/abc/nnm_custompoller/DataParser/scripts/nnm_custompoller.pl`
- **Alerts**: Not monitored

##### Load to BigStreamer cluster
- **Server**: `un2.bigdata.abc.gr`
- **User**: `syzefxis`
- **Scheduler**: `Cron`
- **Schedule**: `Every 30 minutes`
- **Logs**: `/home/users/syzefxis/DataTransformation/log/syzefxis-YYYY-MM-DD.log`
- **Script**: `/home/users/syzefxis/DataTransformation/run/spark-submit.sh`
- **Alerts**: Not monitored

### Form new metrics and categorize KPIs to separate tables
- **Server**: `un2.bigdata.abc.gr`
- **User**: `intra`
- **MySQL User**: `syzeyksis`
- **MySQL Host**: `db-vip.bidata.abc.gr`
- **Scheduler**: `Cron`
- **Schedule**: `Every day at 6:30`
- **Logs**: `/shared/abc/nnmnps/log/nnmnps_Metrics.cron.log`
- **Script**: `/shared/abc/nnmnps/bin/001_CP_nnmnps_Metrics.sh`
- **Alerts**: Not monitored

#### Sqoop Import
- **Server**: `un2.bigdata.abc.gr`
- **User**: `intra`
- **MySQL User**: `syzeyksis`
- **MySQL Host**: `db-vip.bidata.abc.gr`
- **Logs**: `/shared/abc/nnmnps/log/nnmnps_Metrics.cron.log`
- **Script**: `/shared/abc/nnmnps/bin/100_Sqoop_MySql_HDFS_Load.sh`
- **Alerts**: Not monitored

#### Transformation to calculate report daily KPIs
- **User**: `intra`
- **Scheduler**: `Oozie`
- **Schedule**: `Every day at 8:00 (UTC)`
- **Oozie Coordinator**: `DailySyzefxisCoordinator`
- **Oozie workflow**: `Syzefxis_Daily_Spark`
- **Logs**: From Hue go to `Job Browser -> Workflows` and filter with the workflow name
- **Alerts**: Not monitored

#### Transformation to calculate report monthly KPIs
- **User**: `intra`
- **Scheduler**: `Oozie`
- **Schedule**: `Every 1st day of month at 10:00 (UTC)`
- **Oozie Coordinator**: `MonthlySyzefxisCoordinator`
- **Oozie workflow**: `Syzefxis_Monthly_Spark`
- **Logs**: From Hue go to `Job Browser -> Workflows` and filter with the workflow name
- **Alerts**: Not monitored

#### Mail Report
- **Server**: `un2.bigdata.abc.gr`
- **Scheduler**: `Cron`
- **Schedule**: `At the second day of each month at 6:00`
- **User**: `intra`
- **Logs**: `/shared/abc/nnmnps/log/901_Export_CSV_reports.cron.log`
- **Scripts**:
  - `/shared/abc/nnmnps/bin/901_Export_CSV_reports.sh`
  - `/shared/abc/nnmnps/bin/902_Mail_Exported_Files.sh`
- **Export folder**: `/shared/abc/nnmnps/tmp`
- **Alerts**: Not monitored

## 4. Monitoring & Debugging
### Logs
- Logs stored in `/var/logs`

### Troubleshooting

#### Check if the custompoller continuously generates raw files.
1. `ssh ipvpn@un2`
2. `ssh custompoller@nnmprd01` (active node)
3. `cd /home/custompoller/out`
4. `ls -ltr nnmcp.saa-syze1.*.txt`

Example output:

-rw-r--r-- 1 custompoller custompoller 32195036 Jan 16 16:40 nnmcp.saa-syze1.202401161640.txt.LOADED -rw-r--r-- 1 custompoller custompoller 32196182 Jan 16 16:45 nnmcp.saa-syze1.202401161645.txt.LOADED -rw-r--r-- 1 custompoller custompoller 32199664 Jan 16 16:55 nnmcp.saa-syze1.202401161655.txt.LOADED


#### If an old lock file remains, delete it manually.
- Log file: `/home/custompoller/log/syzeyksis-2024-01-10.log`
- Error message:

java.lang.IllegalStateException: Lock file /home/custompoller/out/saa-syze1.lock already exists.

- **Solution**: Delete the lock file manually:

rm /home/custompoller/out/saa-syze1.lock


## 5. Troubleshooting
- Error 101: Fix it by doing X

## 6. Data Validation & Checks

## 7. Miscellaneous Notes
