# Brond ADSL/VDSL Flow

## 1. Overview
This document describes the Brond ADSL/VDSL Flow, detailing its installation, data processing, monitoring, troubleshooting, and data validation.

## 2. Installation & Configuration

### Data Sources
#### FTP Server
- **Host:** `999.999..999.999`
- **Port:** `22`
- **Protocol:** `SFTP`
- **User:** `bigd`
- **Spool Area:** `/ADSL_Brond_DWH`
- **File Type:** `DWH_ADSL*.csv.gz` and `DWH_VDSL*.csv.gz`
- **Load Suffix:** `LOADED`

#### Local FileSystem Directories
- **Node:** `un-vip.bigdata.abc.gr (999.999.999.999)`
- **Landing Zone:** `/data/1/brond_dsl_stats_LZ`
- **Archive Directory:** `/data/1/brond_dsl_stats_LZ/archives`
- **Work Directory:** `/shared/abc/brond_dsl_stats/repo`

#### HDFS Directories
- **HDFS Bin:** `/user/brond`
- **HDFS Directory:** `/ez/warehouse/brond.db/landing_zone/brond_dsl_stats`
- **HDFS Pending Directory:** `/ez/warehouse/brond.db/landing_zone/brond_dsl_stats/not_loaded`
- **HDFS Stats Directory:** `/ez/warehouse/brond.db/landing_zone/brond_dsl_stats/stats`

### Scripts & Configuration
- **Node:** `un-vip.bigdata.abc.gr (999.999.999.999)`
- **User:** `brond`
- **Scripts Path:** `/shared/abc/brond_dsl_stats/DataParser/scripts`
- **Configuration Path:** `/shared/abc/brond_dsl_stats/DataParser/scripts/transferlist/*.trn` (e.g., `brond_dsl_stats.trn`)

### Logs
- **Node:** `un-vip.bigdata.abc.gr (999.999.999.999)`
- **User:** `brond`
- **Path:** `/shared/abc/brond_dsl_stats/DataParser/scripts/log`
- **Log File:** `002.Brond_xDSL_Load.<YYYYMMDD>.log`

### Oozie Scheduling
- **User:** `brond`
- **Coordinator:** `Brond_Load_xDSL_Coord_NEW`
  - **Runs at:** `04:00, 05:00, 06:00, 10:00 UTC`
- **Workflow:** `Brond_Load_xDSL_WF_NEW`
- **Main Script:** `HDFS:/user/brond/000.Brond_xDSL_Oozie_Main.sh`
- **SSH Identity File:** `HDFS:/user/brond/id_rsa`

**Main Script:** Runs `oozie_brond_xdsl.sh` on `un-vip.bigdata.abc.gr` using **ssh** as user **brond**  

ssh -o "StrictHostKeyChecking no" -i ./id_rsa brond@un-vip.bigdata.abc.gr "/shared/abc/brond_dsl_stats/DataParser/scripts/oozie_brond_xdsl.sh"


### Hive Tables
- **Target Database:** `brond`
- **Staging Tables:** `brond.brond_adsl_stats_daily_stg, brond.brond_vdsl_stats_daily_stg`
- **Target Tables:** `brond.brond_adsl_stats_daily, brond.brond_vdsl_stats_daily`

### Beeline & Impala Shell Commands
- **Beeline:**  

/usr/bin/beeline -u "jdbc:hive2://un-vip.bigdata.abc.gr:10000/default;principal=hive/_HOST@CNE.abc.GR;ssl=true;sslTrustStore=/usr/java/latest/jre/lib/security/jssecacerts;trustStorePassword=changeit"

- **Impala-shell:**  

/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k


## 3. Data Processing

### Steps:
1. Fetch raw files (`*.csv.gz`) from the FTP server.
2. Rename raw files by appending the `.LOADED` suffix.
3. Unzip files using `gzip -d`.
4. Parse raw files:
 - Remove headers.
 - Remove double quotes.
 - Extract `PAR_DT` value from the filename.
 - Rename file to `HDFS___<filename>.<load_time>.parsed`.
5. Upload parsed files to HDFS.
6. Clean up local copies of raw files.
7. Load HDFS files into the Hive staging tables:
 - `brond.brond_adsl_stats_daily_stg`
 - `brond.brond_vdsl_stats_daily_stg`
8. Update final tables with filtered columns.

## 4. Monitoring & Debugging

### Logs
- **Logs are stored in:** `/shared/abc/brond_dsl_stats/DataParser/scripts/log`

### Monitoring Connection Details
| Field        | Value               |
|-------------|---------------------|
| Database Type | MySQL |
| Host | `999.999.999.999` |
| DB Name | `monitoring` |
| DB User | `monitoring` |
| Table | `jobstatus` |

**Connection command:**

/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring


### Monitoring Health-Check
Check the monitoring status using:

curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/app/check'

Expected response:

{"code":0,"info":"App is up and running. Current time:20220803 06:46:57.708 +0000"}


## 5. Troubleshooting

- An email will be sent by the system with the point of failure.
- Check the log file for errors:

egrep -i 'error|fail|exception|problem' /shared/abc/brond_dsl_stats/DataParser/scripts/log/002.Brond_xDSL_Load.<YYYYMMDD>.log


- List Failed Monitoring messages:

/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring select * from jobstatus where upper(job) like 'BROND__DSL%' and status='FAILED' and operative_partition=(select max(operative_partition) from jobstatus where upper(job) like 'BROND__DSL%' and operative_partition regexp '[0-9]{8}') order by id;


## 6. Data Validation & Checks

### Check Final Tables for New Partitions

/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k

refresh brond.brond_adsl_stats_daily;
show partitions brond.brond_adsl_stats_daily;
refresh brond.brond_vdsl_stats_daily; show partitions brond.brond_vdsl_stats_daily;


### Check the Amount of Data in Final Tables

/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k

SELECT par_dt, count() as cnt from brond.brond_adsl_stats_daily group by par_dt order by 1; SELECT par_dt, count() as cnt from brond.brond_vdsl_stats_daily group by par_dt order by 1;


## 7. Miscellaneous Notes

- In the event of multiple file transfers, data in the Brond table will be overwritten.
- Responsible teams must ensure proper deletion of files.
