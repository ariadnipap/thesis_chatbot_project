# CSI-Redis Flow

## Installation info

### Data Source
- Source system: HDFS  
  - user : `rediscsi`
  - Parquet files:  
		- `/ez/warehouse/npce.db/yak_cells/*`  
		- `/ez/warehouse/csi.db/csi_cell_dashboard_primary_dly/*`  
		- `/ez/warehouse/csi.db/csi_cell_daily_v3/*`  

- Local FileSystem Directories
  - user : `rediscsi`
	- exec node : defined by Oozie
	- work dir : defined by Oozie
	- export dir: `/csiRedis_exp_data`

- HDFS Directories
	- Export dir : `/user/rediscsi/docx-data/csi/parquet/`
	- Status dir : `/user/rediscsi/docx-data/metatdata/checkpoints`

#### Scripts-Configuration Location
- node : `HDFS`
- user : `rediscsi`
- scripts path : `hdfs:/user/rediscsi`
-	configurations path : `hdfs:/user/rediscsi`

#### Logs Location
- node : `HDFS`
- user : `rediscsi`
- path : `/user/rediscsi/log`
- log file: `csiRedis.<partition data>.<execution ID>.tar.gz`  
	*i.e. `csiRedis.20230420.20230420_230010.tar.gz`*

#### Oozie Scheduling
- user : rediscsi
- Coordinator :`Redis-CSI_Coordinator`  
- Workflow : `Redis-CSI_Workflow`  
- Shell : `/user/rediscsi/100.CSI_Main.sh`
- runs at : `20:00 UTC Daily`

#### Database CLI commands
- Beeline: `/usr/bin/beeline -u "jdbc:hive2://un-vip.bigdata.abc.gr:10000/def_network_map;principal=hive/_HOST@CNE.abc.GR;ssl=true;sslTrustStore=/usr/java/latest/jre/lib/security/jssecacerts;trustStorePassword=changeit"`
- Impala: `/usr/bin/impala-shell -i un-vip.bigdata.abc.gr -d def_network_map --ssl -k`
- MySql*: `mysql -u monitoring -p -h 999.999.999.999 monitoring`

*\*The password for the MySql database can be found [here](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/devpasswd.kdbx)*


### Data target
- Redis VM:`999.999.999.999`
- Port Forward:`un-vip.bigdata.abc.gr:2223`
- user: `bigstreamer`
- scripts path: `/home/bigstreamer/bin`
-	Load Script: `102.CSI_Redis_Load_Data.sh`


## Data process

### Set HDFS Export Path
Defines the export path in HDFS and updates the json configuration files.  
Replaces the key-word `HDFS_PATH_YYYYMMDD` with the `/user/rediscsi/docx-data/csi/parquet/<execution ID>`  
i.e. `/user/rediscsi/docx-data/csi/parquet/20230401_102030`  

### Data Preparation
Execute the Data preparation Spark jobs
- AggregateRdCells  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.aggregator.AggregateRdCells cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./aggregate_rd_cells_full.json`

- AggregateCsiPrimary  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.aggregator.AggregateCsiPrimary cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar aggregate_csi_primary_inc.json`  

**IMPORTANT: if any of the above Spark jobs fails then the procedure stops.**


### Data Aggregation
Execute the Data Aggregation Spark jobs

- CSIAveragePerCellId  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.dashboard.metrics.data.csiarea.CSIAveragePerCellId ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./csi_average_per_cell_id_metrics_predef_all.json`

- AverageCsi  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.dashboard.metrics.data.avgcsi.AverageCsi ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./avg_csi_metrics_predef_all.json`

- PLMNCsiCellDistri  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.dashboard.metrics.data.plmncsicelldistribution.PLMNCsiCellDistri ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./plmn_csi_cell_distri_metrics_predef_all.json`

- TopWorstCsiCellTableAndMap  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.dashboard.metrics.data.topworstcsi.TopWorstCsiCellTableAndMap ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./top_worst_csi_metrics_predef_all.json`

- CSIPerLocTimeCharts  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.dashboard.metrics.data.csibyloc.CSIPerLocTimeChartsToMongo ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./avg_csi_by_loc_metrics_predef_all_mongo.json`

- TopWorstDeltaCsiCellTableAndMap  
`spark-submit --verbose --master yarn --deploy-mode client --principal "rediscsi@CNE.abc.GR" --keytab "./rediscsi.keytab" --jars ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar --class de.telekom.cxi.dashboard.metrics.data.topworstdeltacsi.TopWorstDeltaCsiCellTableAndMap ./cxi-etl-1.0-SNAPSHOT-jar-with-dependencies.jar ./top_worst_delta_csi_metrics_inc.json`

**Ndef: The Spark jobs above create the export file in HDFS under `/user/rediscsi/docx-data/csi/parquet/<execution ID>`**

### Get export files from HDFS
Copy the export files from HDFS to the slave node's local filesystem  
The working slave node is defined by Oozie

	`hdfs dfs -get /user/rediscsi/docx-data/csi/parquet/<execution ID>/* ./csiRedis_exp_data/<execution ID>`  
	i.e. `hdfs dfs -get /user/rediscsi/docx-data/csi/parquet/20230401_102030/* ./csiRedis_exp_data/20230401_102030`  

### Archive export files
creates a compressed tar file which contains all the log files
	`tar cvfz ./csiRedis_exp_data/<execution ID>/redisCSI.<execution ID>.tar.gz ./csiRedis_exp_data/<execution ID>`  
	i.e. `tar cvfz ./csiRedis_exp_data/<execution ID>/redisCSI.20230401_102030.tar.gz ./csiRedis_exp_data/20230401_102030`

### Tranfer Archived file to Redis VM
Tranfers the Archived file to Redis VM using `SFTP PUT`  
`echo "put ./csiRedis_exp_data/<execution ID>/redisCSI.<execution ID>.tar.gz <redis_LZ>" | sftp -o "StrictHostKeyChecking no" -i ./id_rsa -P$<redis_Port> $<redis_User>@$<redis_Node>`  
i.e. `echo "put ./csiRedis_exp_data/20230401_102030/redisCSI.20230401_102030.tar.gz ./CSI_LZ" | sftp -o "StrictHostKeyChecking no" -i ./id_rsa -P2223 bigstreamer@un-vip.bigdata.abc.gr`

### Load Data to Redis DB
Extracts the parquet files from the Archived file and load them into the Redis database  
Execute the load script `Redis VM:/home/bigstreamer/bin/102.CSI_Redis_Load_Data.sh` remdefly.
	`ssh -o "StrictHostKeyChecking no" -i ./id_rsa -P2223 bigstreamer@un-vip.bigdata.abc.gr "/home/bigstreamer/bin/102.CSI_Redis_Load_Data.sh`


## Monitoring

### Monitoring connection details
|Field|Value|
|-|-|
|Database Type| mysql  
|Host| 999.999.999.999  
|DB Name| monitoring  
|DB User| monitoring  
|Table| jobstatus  


### Monitoring Message list
For each load the following set of messages will be recorded in the Monitoring database.
```
+-----------------+---------------------------------+------------------+---------------------+---------+-------------------------+
| execution_id    | component                       | job              | operative_partition | status  | system_ts               |
+-----------------+---------------------------------+------------------+---------------------+---------+-------------------------+
| 20230420_230010 | MAIN_START                      | JOB_BEGIN        | 20230420            | SUCCESS | 2023-04-20 23:00:10.000 |
| 20230420_230010 | UPDATE_HDFS_EXPORT_PATH         | PRE_TASK         | 20230420            | SUCCESS | 2023-04-20 23:00:10.000 |
| 20230420_230010 | AGGREGATERDCELLS                | DATA_PREPARATION | 20230420            | SUCCESS | 2023-04-20 23:02:14.000 |
| 20230420_230010 | AGGREGATECSIPRIMARY             | DATA_PREPARATION | 20230420            | SUCCESS | 2023-04-20 23:06:30.000 |
| 20230420_230010 | COREKPIANDCSIBYLEVEL            | DATA_AGGREGATION | 20230420            | SUCCESS | 2023-04-20 23:09:29.000 |
| 20230420_230010 | CSIAVERAGEPERCELLID             | DATA_AGGREGATION | 20230420            | SUCCESS | 2023-04-20 23:12:14.000 |
| 20230420_230010 | AVERAGECSI                      | DATA_AGGREGATION | 20230420            | SUCCESS | 2023-04-20 23:15:49.000 |
| 20230420_230010 | PLMNCSICELLDISTRI               | DATA_AGGREGATION | 20230420            | SUCCESS | 2023-04-20 23:17:17.000 |
| 20230420_230010 | TOPWORSTCSICELLTABLEANDMAP      | DATA_AGGREGATION | 20230420            | SUCCESS | 2023-04-20 23:24:42.000 |
| 20230420_230010 | CSIPERLOCTIMECHARTSTOMONGO      | DATA_AGGREGATION | 20230420            | SUCCESS | 2023-04-20 23:27:58.000 |
| 20230420_230010 | TOPWORSTDELTACSICELLTABLEANDMAP | DATA_AGGREGATION | 20230420            | SUCCESS | 2023-04-20 23:29:34.000 |
| 20230420_230010 | GET_EXP_FILES_FROM_HDFS         | POST_TASK        | 20230420            | SUCCESS | 2023-04-20 23:29:55.000 |
| 20230420_230010 | TAR_EXP_FILES                   | POST_TASK        | 20230420            | SUCCESS | 2023-04-20 23:30:09.000 |
| 20230420_230010 | SFTP_PUT_EXP_FILE_TO_REDIS      | POST_TASK        | 20230420            | SUCCESS | 2023-04-20 23:30:13.000 |
| 20230420_230010 | LOAD_DATA_TO_REDIS_DB           | LOAD_REDIS       | 20230420            | SUCCESS | 2023-04-20 23:33:52.000 |
| 20230420_230010 | MAIN_END                        | JOB_END          | 20230420            | SUCCESS | 2023-04-20 23:36:01.000 |
+-----------------+---------------------------------+------------------+---------------------+---------+-------------------------+
```

### Monitoring Component list
```
+---------------------------------+------------------+--------------------------------------------------------------------------------------------------
| Component                       | Job              | Description
+---------------------------------+------------------+--------------------------------------------------------------------------------------------------
| MAIN_START                      | JOB_BEGIN        | Procedure Started
| UPDATE_HDFS_EXPORT_PATH         | PRE_TASK         | Set the HDFS path in Json Configuration files
| AGGREGATERDCELLS                | DATA_PREPARATION | Data preparation: `spark-submit` using `aggregate_rd_cells_full.json` config file
| AGGREGATECSIPRIMARY             | DATA_PREPARATION | Data preparation: `spark-submit` using `aggregate_csi_primary_inc.json` config file
| COREKPIANDCSIBYLEVEL            | DATA_AGGREGATION | Data aggregation: `spark-submit` using `core_kpi_and_csi_by_level_metrics_predef_all` config file
| CSIAVERAGEPERCELLID             | DATA_AGGREGATION | Data aggregation: `spark-submit` using `csi_average_per_cell_id_metrics_predef_all` config file
| AVERAGECSI                      | DATA_AGGREGATION | Data aggregation: `spark-submit` using `avg_csi_metrics_predef_all` config file
| PLMNCSICELLDISTRI               | DATA_AGGREGATION | Data aggregation: `spark-submit` using `plmn_csi_cell_distri_metrics_predef_all` config file
| TOPWORSTCSICELLTABLEANDMAP      | DATA_AGGREGATION | Data aggregation: `spark-submit` using `top_worst_csi_metrics_predef_all` config file
| CSIPERLOCTIMECHARTSTOMONGO      | DATA_AGGREGATION | Data aggregation: `spark-submit` using `avg_csi_by_loc_metrics_predef_all_mongo` config file
| TOPWORSTDELTACSICELLTABLEANDMAP | DATA_AGGREGATION | Data aggregation: `spark-submit` using `top_worst_delta_csi_metrics_inc` config file
| GET_EXP_FILES_FROM_HDFS         | POST_TASK        | hdfs copyToLocal the export files
| TAR_EXP_FILES                   | POST_TASK        | Archive the export files
| SFTP_PUT_EXP_FILE_TO_REDIS      | POST_TASK        | Tranfers the Archived file to Redis VM
| LOAD_DATA_TO_REDIS_DB           | LOAD_REDIS       | Upload the Archived file into Redis database 
| MAIN_END                        | JOB_END          | Procedure Completed
+---------------------------------+------------------+--------------------------------------------------------------------------------------------------
```

### Monitoring database Queries
- List messages of the last load  
	`/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`

	```
    select 
      execution_id, component, job, operative_partition,  
      status, system_ts, substr(message,1,50) msg
    from jobstatus a where 1=1
    and upper(application)='CSI'
    and execution_id in (select max(execution_id) from jobstatus where upper(application)='CSI' and upper(job)='DATA_PREPARATION')
    order by a.id
    ;
	```

### Monitoring Health-Check
  - Check Monitoring status.  
	```	
	$ curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/app/check'
	
	{"code":0,"info":"App is up and running. Current time:20220803 06:46:57.708 +0000"}
	```  
	
	- In case of Monitoring is stopped then follow the instructions of `start monitoring-app` procedure described in [Monitoring application](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/BigStreamer/supportDocuments/procedures/manage-monitoring-app.md#procedure) doc

## Troubleshooting
An email will be sent by the system with the point of failure.  
i.e.
<pre>
From: abc_bigd@abc.gr  
Subject: CSI - DATA_AGGREGATION: FAILED  

<b>
Data preparation:top_worst_delta_csi_metrics_inc
Exec_id:20230401_102030
</b>
This is an automated e-mail.  
Please do not reply.  
</pre>


**Actions**  
1. Write down the value of `Exec_id` described in the alert email  
	i.e. Exec_id:`1673849411`

2. Log files are stored in HDFS in archived files.  
```
$ hdfs dfs -ls /user/rediscsi/log/

-rw-r--r--   3 rediscsi rediscsi  366865842 2023-04-20 23:35 /user/rediscsi/log/csiRedis.20230420.20230420_230010.tar.gz
-rw-r--r--   3 rediscsi rediscsi  361801963 2023-04-21 23:38 /user/rediscsi/log/csiRedis.20230421.20230421_230010.tar.gz
-rw-r--r--   3 rediscsi rediscsi  358913487 2023-04-22 23:41 /user/rediscsi/log/csiRedis.20230422.20230422_230013.tar.gz
-rw-r--r--   3 rediscsi rediscsi  364564867 2023-04-23 23:42 /user/rediscsi/log/csiRedis.20230423.20230423_230010.tar.gz
-rw-r--r--   3 rediscsi rediscsi  359603322 2023-04-24 23:38 /user/rediscsi/log/csiRedis.20230424.20230424_230009.tar.gz
```
Each archived file contains a set of logs related to the specific flow run (execution ID).  
The filename contains info about the `<partition data>` and the `<execution ID>`  
`csiRedis.<partition data>.<execution ID>.tar.gz`

3. Get the log file  
- create a new dir to store the log file
	```
	mkdir -p /tmp/csi_redis_log
	cd /tmp/csi_redis_log
	```

- Copy from the HDFS log dir the proper log file according to the `<execution ID>` mentioned in the alert email
`hdfs dfs -get /user/rediscsi/log/csiRedis.20230401.20230401_102030.tar.gz`

- Extract the archived log file
`tar xvfz ${archFile} --strip-components 9 -C .`

- Searches for Exception messages in log files  
`egrep -i '(Exception:|Coused by)' *.log`  

4. In case of failure, the flow will try to load the data in the next run.  
	jkl-Telecom is not aware of how the data files are produced or the contents in them.  
	The Spark jobs that are used by the flow, have been developed by a partner of abc (an India company).  

	jkl-Telecom is responsible for 
	- the execution of Spark jobs to produce the export data files, 
	- the collection of the export data files (if any), 
	- the transfer of them in Redis node 
	- and finally the loading of the export files into the Redis database (using specific Spark jobs).
