# CSI-Redis Flow

## 1. Overview

`CSI-Redis Flow` is a data pipeline that processes, aggregates, and transfers CSI-related data from HDFS to Redis. It involves multiple Spark jobs for data preparation, aggregation, and exporting files to a Redis VM for further analysis.

**Key Information**
- **User:** `rediscsi`
- **Execution Schedule:** `20:00 UTC Daily`
- **Primary Storage:** HDFS
- **Data Processing Framework:** Spark
- **Log Storage:** HDFS (`/user/rediscsi/log`)
- **Primary Scripting Language:** Shell & SQL
- **Monitoring System:** MySQL, Grafana

## 2. Installation & Configuration

### 2.1. Scripts & Configuration
#### Data Sources
- **Source System:** HDFS  
  - **User:** `rediscsi`
  - **Parquet Files:**
    - `/ez/warehouse/npce.db/yak_cells/*`
    - `/ez/warehouse/csi.db/csi_cell_dashboard_primary_dly/*`
    - `/ez/warehouse/csi.db/csi_cell_daily_v3/*`

- **Local File System Directories**
  - **User:** `rediscsi`
  - **Exec Node:** Defined by Oozie
  - **Work Dir:** Defined by Oozie
  - **Export Dir:** `/csiRedis_exp_data`

- **HDFS Directories**
  - **Export Dir:** `/user/rediscsi/docx-data/csi/parquet/`
  - **Status Dir:** `/user/rediscsi/docx-data/metatdata/checkpoints`

#### Scripts & Configuration Location
- **Node:** `HDFS`
- **User:** `rediscsi`
- **Scripts Path:** `hdfs:/user/rediscsi`
- **Configuration Path:** `hdfs:/user/rediscsi`

#### Logs Location
- **Node:** `HDFS`
- **User:** `rediscsi`
- **Log Path:** `/user/rediscsi/log`
- **Log File Pattern:** `csiRedis.<partition data>.<execution ID>.tar.gz`
  - Example: `csiRedis.20230420.20230420_230010.tar.gz`

#### Oozie Scheduling
- **User:** `rediscsi`
- **Coordinator:** `Redis-CSI_Coordinator`
- **Workflow:** `Redis-CSI_Workflow`
- **Shell Script:** `/user/rediscsi/100.CSI_Main.sh`
- **Execution Time:** `20:00 UTC Daily`

#### Database CLI Commands
- **Beeline:**  

/usr/bin/beeline -u "jdbc:hive2://un-vip.bigdata.abc.gr:10000/def_network_map;principal=hive/_HOST@CNE.abc.GR;ssl=true;sslTrustStore=/usr/java/latest/jre/lib/security/jssecacerts;trustStorePassword=changeit"

- **Impala:**  

/usr/bin/impala-shell -i un-vip.bigdata.abc.gr -d def_network_map --ssl -k

- **MySQL:**  

mysql -u monitoring -p -h 999.999.999.999 monitoring

*Password can be found [here](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/devpasswd.kdbx).*

### 2.2. Data Target
- **Redis VM:** `999.999.999.999`
- **Port Forwarding:** `un-vip.bigdata.abc.gr:2223`
- **User:** `bigstreamer`
- **Scripts Path:** `/home/bigstreamer/bin`
- **Load Script:** `102.CSI_Redis_Load_Data.sh`

## 3. Data Processing

### 3.1. Set HDFS Export Path
Defines the export path in HDFS and updates the JSON configuration files.  
Replaces `HDFS_PATH_YYYYMMDD` with `/user/rediscsi/docx-data/csi/parquet/<execution ID>`.  

Example:  

/user/rediscsi/docx-data/csi/parquet/20230401_102030


### 3.2. Data Preparation
Execute the data preparation Spark jobs:
- **AggregateRdCells**  

spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --class de.telekom.cxi.aggregator.AggregateRdCells cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./aggregate_rd_cells_full.json

- **AggregateCsiPrimary**  

spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --class de.telekom.cxi.aggregator.AggregateCsiPrimary cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar aggregate_csi_primary_inc.json


### 3.3. Data Aggregation
Run Spark jobs for data aggregation:

spark-submit --class de.telekom.cxi.dashboard.metrics.data.csiarea.CSIAveragePerCellId ... spark-submit --class de.telekom.cxi.dashboard.metrics.data.avgcsi.AverageCsi ... spark-submit --class de.telekom.cxi.dashboard.metrics.data.topworstcsi.TopWorstCsiCellTableAndMap ...


### 3.4. Export & Transfer
- **Retrieve export files from HDFS**

hdfs dfs -get /user/rediscsi/docx-data/csi/parquet/<execution ID>/* ./csiRedis_exp_data/<execution ID>

- **Archive files**

tar cvfz ./csiRedis_exp_data/<execution ID>/redisCSI.<execution ID>.tar.gz ./csiRedis_exp_data/<execution ID>

- **Transfer archived files to Redis VM**

echo "put ./csiRedis_exp_data/<execution ID>/redisCSI.<execution ID>.tar.gz <redis_LZ>" | sftp ...

- **Load data into Redis DB**

ssh bigstreamer@un-vip.bigdata.abc.gr "/home/bigstreamer/bin/102.CSI_Redis_Load_Data.sh"


## 4. Monitoring & Debugging

### 4.1. Logs
- **Log Location:** `/user/rediscsi/log`
- **Retrieve logs from HDFS:**

hdfs dfs -get /user/rediscsi/log/csiRedis.<execution ID>.tar.gz


### 4.2. Monitoring
- **Check monitoring app for success:**

curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=CSI&job=DATA_AGGREGATION&status=SUCCESS'

- **Check for failures:**

curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=CSI&job=DATA_AGGREGATION&status=FAILED'


## 5. Troubleshooting

### Common Errors & Fixes
- **Failed Data Preparation**
- Check if Spark jobs are failing due to missing configuration.
- Ensure HDFS paths are accessible.
- **SFTP Transfer Failure**
- Validate `ssh.host` and `ssh.user` settings.
- **HDFS Export Path Issue**
- Confirm if `/user/rediscsi/docx-data/csi/parquet/` exists.

## 6. Data Validation & Checks

### 6.1. Monitoring Components

+-----------------+---------------------------------+------------------+ | execution_id | component | status | +-----------------+---------------------------------+------------------+ | 20230420_230010 | AGGREGATERDCELLS | SUCCESS | | 20230420_230010 | CSIAVERAGEPERCELLID | SUCCESS | +-----------------+---------------------------------+------------------+


### 6.2. Grafana Dashboard
- **URL:**  

https://unc1.bigdata.abc.gr:3000/d/DNM-sBo4z/dwhfixed-dashboard


## 7. Miscellaneous Notes

- Ensure proper execution of Spark jobs before transferring files.
- Check logs frequently for debugging.
- In case of persistent failures, contact the **BigData Developer Team**.
