# Brond ADSL/VDSL Flow

- [Brond Retrains Flow](brond-retrains-flow)
	- [Installation info](#installation-info)
		- [Data Source File](#data-source-file)
		- [Scripts-Configuration Location](#scripts-configuration-location)
		- [Logs Location](#logs-location)
		- [Oozie Scheduling](#oozie-scheduling)
		- [Hive Tables](#hive-tables)
		- [Beeline-Impala Shell commands](#beeline-impala-shell-commands)
	- [Data process](#data-process)
	- [Monitoring](#monitoring)
		- [Monitoring connection details](#monitoring-connection-details)
		- [Monitoring Message list](#monitoring-message-list)
		- [Monitoring Component list](#monitoring-component-list)
		- [Monitoring database Queries](#monitoring-database-queries)
		- [Monitoring Health-Check](#monitoring-health-check)
	- [Troubleshooting](#troubleshooting)
		- [Common errors](#common-errors)
	- [Data Check](#data-check)


## Installation info

### Data Source File
- Source system: FTP Server  
  - host :`999.999.999.999`
  - port :`22`
  - protocol :`SFTP`
  - user : `bigd`
  - spool area : `/ADSL_Brond_DWH`
  - file_type : `DWH_ADSL*.csv.gz` and `DWH_VDSL*.csv.gz`
  - load_suffix : `LOADED`

- Local FileSystem Directories
	- node : `un-vip.bigdata.abc.gr (999.999.999.999)`
	- landing_zone : `/data/1/brond_dsl_stats_LZ`
	- archive_dir= : `/data/1/brond_dsl_stats_LZ/archives`
	- work_dir= : `/shared/abc/brond_dsl_stats/repo`

- HDFS Directories
	- hdfs_Bin : `/user/brond`
	- hdfs_dir : `/ez/warehouse/brond.db/landing_zone/brond_dsl_stats`
	- hdfs_pending_dir : `/ez/warehouse/brond.db/landing_zone/brond_dsl_stats/not_loaded`
	- hdfs_stats_dir : `/ez/warehouse/brond.db/landing_zone/brond_dsl_stats/stats`


### Scripts-Configuration Location
- node : `un-vip.bigdata.abc.gr (999.999.999.999)`
- user : `brond`
- scripts path : `/shared/abc/brond_dsl_stats/DataParser/scripts`
-	configurations path : `/shared/abc/brond_dsl_stats/DataParser/scripts/transferlist/*.trn` (i.e. brond_retrains.trn)

### Logs Location
- node : `un-vip.bigdata.abc.gr (999.999.999.999)`
- user : `brond`
- path : `/shared/abc/brond_dsl_stats/DataParser/scripts/log`
- log file: `002.Brond_xDSL_Load.<YYYYMMDD>.log`

### Oozie Scheduling
- user : `brond`
- Coordinator :`Brond_Load_xDSL_Coord_NEW`  
	runs at : `04:00, 05:00, 06:00, 10:00 UTC`
- Workflow : `Brond_Load_xDSL_WF_NEW`  
- Main script : `HDFS:/user/brond/000.Brond_xDSL_Oozie_Main.sh`
- SSH Identity file : `HDFS:/user/brond/id_rsa`

Ndef: **Main Script** runs `oozie_brond_xdsl.sh` located on `un-vip.bigdata.abc.gr` using **ssh** as user **brond**  
`$ ssh -o "StrictHostKeyChecking no" -i ./id_rsa brond@un-vip.bigdata.abc.gr "/shared/abc/brond_dsl_stats/DataParser/scripts/oozie_brond_xdsl.sh"`

### Hive Tables
- Target Database: `brond`
- Staging Tables: `brond.brond_adsl_stats_daily_stg, brond.brond_vdsl_stats_daily_stg`
- Target Tables: `brond.brond_adsl_stats_daily, brond.brond_vdsl_stats_daily`

### Beeline-Impala Shell commands
- Beeline: `/usr/bin/beeline -u "jdbc:hive2://un-vip.bigdata.abc.gr:10000/default;principal=hive/_HOST@CNE.abc.GR;ssl=true;sslTrustStore=/usr/java/latest/jre/lib/security/jssecacerts;trustStorePassword=changeit"`
- Impala-shell: `/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k`


## Data process

1. sftp get raw files (*.csv.gz) from FTP Server to `/data/1/brond_dsl_stats_LZ`
```
echo "ls -l ADSL_Brond_DWH" | sftp bigd@999.999.999.999

sftp> ls -l ADSL_Brond_DWH
-rw-r--r--    0 507      500      35399779 Nov 27 06:19 ADSL_Brond_DWH/DWH_ADSL.327_2022_11_27.csv.gz.LOADED
-rw-r--r--    0 507      500      35440542 Nov 28 06:57 ADSL_Brond_DWH/DWH_ADSL.328_2022_11_28.csv.gz.LOADED
-rw-r--r--    0 507      500      35360378 Nov 29 06:20 ADSL_Brond_DWH/DWH_ADSL.329_2022_11_29.csv.gz.LOADED
-rw-r--r--    0 507      500      35415258 Nov 30 06:48 ADSL_Brond_DWH/DWH_ADSL.330_2022_11_30.csv.gz

-rw-r--r--    0 507      500      150757798 Nov 27 05:33 ADSL_Brond_DWH/DWH_VDSL.327_2022_11_27.csv.gz.LOADED
-rw-r--r--    0 507      500      150728306 Nov 28 06:26 ADSL_Brond_DWH/DWH_VDSL.328_2022_11_28.csv.gz.LOADED
-rw-r--r--    0 507      500      150589497 Nov 29 05:34 ADSL_Brond_DWH/DWH_VDSL.329_2022_11_29.csv.gz.LOADED
-rw-r--r--    0 507      500      150823890 Nov 30 06:21 ADSL_Brond_DWH/DWH_VDSL.330_2022_11_30.csv.gz
```
2. rename the raw file(s) in remdef SFTP server by adding the suffix .LOADED
	`echo "rename /ADSL_Brond_DWH/ADSL_Brond_DWH/DWH_ADSL.330_2022_11_30.csv.gz /ADSL_Brond_DWH/ADSL_Brond_DWH/DWH_ADSL.330_2022_11_30.csv.gz.LOADED" | sftp -oport=22 bigd@999.999.999.999`
	`echo "rename /ADSL_Brond_DWH/VDSL_Brond_DWH/DWH_ADSL.330_2022_11_30.csv.gz /ADSL_Brond_DWH/VDSL_Brond_DWH/DWH_ADSL.330_2022_11_30.csv.gz.LOADED" | sftp -oport=22 bigd@999.999.999.999`
3. parsing raw files in `/data/1/brond_dsl_stats_LZ`
	- removes the headers (1st line)
	- removes double-qudefs chars
	- defines the PAR_DT value from the filename (i.e. DWH_ADSL.330_2022_11_30.csv.gz convert to 20221130)
	- add the prefix `HDFS___` to raw file
	- add the suffix `<load time>` to raw file  
		Load time format:`<YYYYMMDD_HHMISS>`  
		i.e. `HDFS___DWH_ADSL.330_2022_11_30.csv.gz.20221201_060005.gz`

4. put raw files into HDFS landingzone
	```
	hdfs dfs -put /data/1/brond_dsl_stats_LZ/HDFS___DWH_ADSL.330_2022_11_30.csv.gz.20221201_060005.gz /ez/warehouse/brond.db/landing_zone/brond_dsl_stats/HDFS___DWH_ADSL.330_2022_11_30.csv.gz.20221201_060005.gz`
	hdfs dfs -put /data/1/brond_dsl_stats_LZ/HDFS___DWH_VDSL.330_2022_11_30.csv.gz.20221201_060005.gz /ez/warehouse/brond.db/landing_zone/brond_dsl_stats/HDFS___DWH_VDSL.330_2022_11_30.csv.gz.20221201_060005.gz`
	```
5. clean-up any copy of the raw files from local filesystem  
	`/data/1/brond_dsl_stats_LZ`  
	`/shared/abc/brond_dsl_stats/repo`  

6. load HDFS files into hive staging tables  
	`brond.brond_adsl_stats_daily_stg` and `brond.brond_vdsl_stats_daily_stg`  
	```
	beeline -e "LOAD DATA INPATH '/ez/warehouse/brond.db/landing_zone/brond_dsl_stats/HDFS___DWH_ADSL.330_2022_11_30.csv.gz.20221201_060005.gz' OVERWRITE INTO TABLE brond.brond_adsl_stats_daily_stg PARTITION (par_dt='20221130')"
	beeline -e "LOAD DATA INPATH '/ez/warehouse/brond.db/landing_zone/brond_dsl_stats/HDFS___DWH_VDSL.330_2022_11_30.csv.gz.20221201_060005.gz' OVERWRITE INTO TABLE brond.brond_vdsl_stats_daily_stg PARTITION (par_dt='20221130')"
	```
	*Ndef: Once the load completed, the staging tables should contain no data.*
	
7. update hive tables with filtered columns  
	script: `/shared/abc/brond_dsl_stats/DataParser/scripts/003.Brond_xDSL_Post.sh`
	
	- `brond_adsl_stats_daily`
		```
		set hive.exec.dynamic.partition.mode=nonstrict;
		insert overwrite table brond.brond_adsl_stats_daily partition (par_dt) 
		select 
			serv_tel,
			serv_siid,
			ne_name,
			ne_port,
			card_tehn,
			card_type,
			inv_port,
			measure_date,
			last_change,
			aif_adm,
			aif_oper,
			opmod_annex,
			up_sign_attn,
			up_snr,
			up_crt_rate,
			up_max_rate,
			dn_sign_attn,
			dn_snr,
			dn_crt_rate,
			dn_max_rate,
			prf_name,
			radius,
			sproto,
			par_dt
		from brond.brond_adsl_stats_daily_stg 
		where 1=1
		;
		```

	- `brond_vdsl_stats_daily`
		```
		set hive.exec.dynamic.partition.mode=nonstrict;
		insert overwrite table brond.brond_vdsl_stats_daily partition (par_dt) 
		select 
			serv_tel,
			serv_siid,
			ne_name,
			ne_port,
			card_tehn,
			card_type,
			inv_port,
			measure_date,
			custid,
			last_change,
			aif_adm,
			aif_oper,
			opmod_annex,
			up_sign_attn,
			up_snr,
			up_max_rate,
			up_crt_rate,
			dn_sign_attn,
			dn_snr,
			dn_max_rate,
			dn_crt_rate,
			prf_name,
			radius,
			sproto,
			par_dt
		from brond.brond_vdsl_stats_daily_stg 
		where 1=1
		;
		```

In the event where multiple files are transfered (files refer to the same data), we proceed with overwriting data in brond table. Deletion of those multiple files is abc's responsibility.


## Monitoring

### Monitoring connection details
|Field|Value|
|-|-|
|Database Type| mysql  
|Host| 999.999.999.999  
|DB Name| monitoring  
|DB User| monitoring  
|Table| jobstatus  

Connection command: `/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`

### Monitoring Message list
For each type of load (ADSL or VDSL) the following set of messages will be recorded in the Monitoring database.
```
id    | execution_id | application | job              | component                                | operative_partition | status  | system_ts           | system_ts_end       | message                | user  | host                  
------+--------------+-------------+------------------+------------------------------------------+---------------------+---------+---------------------+---------------------+------------------------+-------+-----------------------
15675 | 1659931204   | BROND       | BROND_ADSL_STATS | MAIN                                     | 20220808            | SUCCESS | 2022-08-08 07:00:04 | 2022-08-08 07:01:38 | Succesfully Completed. | brond | un2.bigdata.abc.gr
15677 | 1659931204   | BROND       | BROND_ADSL_STATS | GET RAW XDSL FILES                       | 20220808            | SUCCESS | 2022-08-08 07:00:05 |                     | Single raw file found  | brond | un2.bigdata.abc.gr
15679 | 1659931204   | BROND       | BROND_ADSL_STATS | RENAME FILES @SFTP SERVER                | 20220808            | SUCCESS | 2022-08-08 07:00:06 |                     |                        | brond | un2.bigdata.abc.gr
15681 | 1659931204   | BROND       | BROND_ADSL_STATS | PARSING FILES                            | 20220808            | SUCCESS | 2022-08-08 07:00:06 |                     |                        | brond | un2.bigdata.abc.gr
15683 | 1659931204   | BROND       | BROND_ADSL_STATS | LOAD HDFS LANDINGZONE                    | 20220808            | SUCCESS | 2022-08-08 07:00:13 |                     |                        | brond | un2.bigdata.abc.gr
15685 | 1659931204   | BROND       | BROND_ADSL_STATS | CLEAN-UP THE INPUT FILES                 | 20220808            | SUCCESS | 2022-08-08 07:00:13 |                     |                        | brond | un2.bigdata.abc.gr
15687 | 1659931204   | BROND       | BROND_ADSL_STATS | LOAD HDFS FILES INTO HIVE STAGING TABLES | 20220808            | SUCCESS | 2022-08-08 07:00:26 |                     |                        | brond | un2.bigdata.abc.gr
15689 | 1659931204   | BROND       | BROND_ADSL_STATS | UPDATE HIVE TABLES WITH FILTERED COLUMNS | 20220808            | SUCCESS | 2022-08-08 07:01:38 |                     |                        | brond | un2.bigdata.abc.gr

id    | execution_id | application | job              | component                                | operative_partition | status  | system_ts           | system_ts_end       | message                | user  | host                  
------+--------------+-------------+------------------+------------------------------------------+---------------------+---------+---------------------+---------------------+------------------------+-------+-----------------------
15691 | 1659931204   | BROND       | BROND_VDSL_STATS | MAIN                                     | 20220808            | SUCCESS | 2022-08-08 07:01:38 | 2022-08-08 07:03:51 | Succesfully Completed. | brond | un2.bigdata.abc.gr
15693 | 1659931204   | BROND       | BROND_VDSL_STATS | GET RAW XDSL FILES                       | 20220808            | SUCCESS | 2022-08-08 07:01:40 |                     | Single raw file found  | brond | un2.bigdata.abc.gr
15695 | 1659931204   | BROND       | BROND_VDSL_STATS | RENAME FILES @SFTP SERVER                | 20220808            | SUCCESS | 2022-08-08 07:01:41 |                     |                        | brond | un2.bigdata.abc.gr
15697 | 1659931204   | BROND       | BROND_VDSL_STATS | PARSING FILES                            | 20220808            | SUCCESS | 2022-08-08 07:01:41 |                     |                        | brond | un2.bigdata.abc.gr
15699 | 1659931204   | BROND       | BROND_VDSL_STATS | LOAD HDFS LANDINGZONE                    | 20220808            | SUCCESS | 2022-08-08 07:01:51 |                     |                        | brond | un2.bigdata.abc.gr
15701 | 1659931204   | BROND       | BROND_VDSL_STATS | CLEAN-UP THE INPUT FILES                 | 20220808            | SUCCESS | 2022-08-08 07:01:51 |                     |                        | brond | un2.bigdata.abc.gr
15703 | 1659931204   | BROND       | BROND_VDSL_STATS | LOAD HDFS FILES INTO HIVE STAGING TABLES | 20220808            | SUCCESS | 2022-08-08 07:02:05 |                     |                        | brond | un2.bigdata.abc.gr
15705 | 1659931204   | BROND       | BROND_VDSL_STATS | UPDATE HIVE TABLES WITH FILTERED COLUMNS | 20220808            | SUCCESS | 2022-08-08 07:03:51 |                     |                        | brond | un2.bigdata.abc.gr
```

### Monitoring Component list
|Component | Description 
|-|-|
|MAIN|Indicates the status of the whole load. <br />Status:RUNNING, SUCCESS, FAILED| 
|GET RAW XDSL FILES|sftp-get the raw files from the remdef server.<br />i.e.<br />DWH_ADSL.197_2022_07_18.csv.gz<br />DWH_VDSL.197_2022_07_18.csv.gz
|RENAME FILES @SFTP SERVER| Rename the raw files in remdef server by adding the suffix .LOADED<br />i.e.<br />DWH_ADSL.197_2022_07_18.csv.gz.LOADED<br />DWH_VDSL.197_2022_07_18.csv.gz.LOADED
|PARSING FILES| removes any control chars (if any) from the raw files
|LOAD HDFS LANDINGZONE|PUT the parsing files into HDFS
|CLEAN-UP THE INPUT FILES|Clean-up any copy of the raw files from the filesystem
|LOAD HDFS FILES INTO HIVE STAGING TABLES| Load raw data (files) into the staging tables<br />`brond.brond_adsl_stats_daily_stg`<br />`brond.brond_vdsl_stats_daily_stg`
|UPDATE HIVE TABLES WITH FILTERED COLUMNS| Update final tables with the necessary columns only.<br />`brond.brond_adsl_stats_daily`<br />`brond.brond_vdsl_stats_daily`

### Monitoring database Queries
- List messages of the last load  
	`/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`

```
select 
  execution_id, id, application, job, component, operative_partition,  
  status, system_ts, system_ts_end, message, user,host   
from jobstatus a where upper(job) like 'BROND__DSL%'   
and execution_id=(select max(execution_id) from jobstatus where upper(job) like 'BROND__DSL%')  
;

execution_id | id    | application | job              | component                                | operative_partition | status  | system_ts           | system_ts_end       | message                | user  | host                  
-------------+-------+-------------+------------------+------------------------------------------+---------------------+---------+---------------------+---------------------+------------------------+-------+-----------------------
1659931204   | 15675 | BROND       | BROND_ADSL_STATS | MAIN                                     | 20220808            | SUCCESS | 2022-08-08 07:00:04 | 2022-08-08 07:01:38 | Succesfully Completed. | brond | un2.bigdata.abc.gr
1659931204   | 15677 | BROND       | BROND_ADSL_STATS | GET RAW XDSL FILES                       | 20220808            | SUCCESS | 2022-08-08 07:00:05 |                     | Single raw file found  | brond | un2.bigdata.abc.gr
1659931204   | 15679 | BROND       | BROND_ADSL_STATS | RENAME FILES @SFTP SERVER                | 20220808            | SUCCESS | 2022-08-08 07:00:06 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15681 | BROND       | BROND_ADSL_STATS | PARSING FILES                            | 20220808            | SUCCESS | 2022-08-08 07:00:06 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15683 | BROND       | BROND_ADSL_STATS | LOAD HDFS LANDINGZONE                    | 20220808            | SUCCESS | 2022-08-08 07:00:13 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15685 | BROND       | BROND_ADSL_STATS | CLEAN-UP THE INPUT FILES                 | 20220808            | SUCCESS | 2022-08-08 07:00:13 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15687 | BROND       | BROND_ADSL_STATS | LOAD HDFS FILES INTO HIVE STAGING TABLES | 20220808            | SUCCESS | 2022-08-08 07:00:26 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15689 | BROND       | BROND_ADSL_STATS | UPDATE HIVE TABLES WITH FILTERED COLUMNS | 20220808            | SUCCESS | 2022-08-08 07:01:38 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15691 | BROND       | BROND_VDSL_STATS | MAIN                                     | 20220808            | SUCCESS | 2022-08-08 07:01:38 | 2022-08-08 07:03:51 | Succesfully Completed. | brond | un2.bigdata.abc.gr
1659931204   | 15693 | BROND       | BROND_VDSL_STATS | GET RAW XDSL FILES                       | 20220808            | SUCCESS | 2022-08-08 07:01:40 |                     | Single raw file found  | brond | un2.bigdata.abc.gr
1659931204   | 15695 | BROND       | BROND_VDSL_STATS | RENAME FILES @SFTP SERVER                | 20220808            | SUCCESS | 2022-08-08 07:01:41 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15697 | BROND       | BROND_VDSL_STATS | PARSING FILES                            | 20220808            | SUCCESS | 2022-08-08 07:01:41 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15699 | BROND       | BROND_VDSL_STATS | LOAD HDFS LANDINGZONE                    | 20220808            | SUCCESS | 2022-08-08 07:01:51 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15701 | BROND       | BROND_VDSL_STATS | CLEAN-UP THE INPUT FILES                 | 20220808            | SUCCESS | 2022-08-08 07:01:51 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15703 | BROND       | BROND_VDSL_STATS | LOAD HDFS FILES INTO HIVE STAGING TABLES | 20220808            | SUCCESS | 2022-08-08 07:02:05 |                     |                        | brond | un2.bigdata.abc.gr
1659931204   | 15705 | BROND       | BROND_VDSL_STATS | UPDATE HIVE TABLES WITH FILTERED COLUMNS | 20220808            | SUCCESS | 2022-08-08 07:03:51 |                     |                        | brond | un2.bigdata.abc.gr
-------------+-------+-------------+------------------+------------------------------------------+---------------------+---------+---------------------+---------------------+------------------------+-------+-----------------------
```

### Monitoring Health-Check
  - Check Monitoring status.  
	```	
	$ curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/app/check'
	
	{"code":0,"info":"App is up and running. Current time:20220803 06:46:57.708 +0000"}
	```  
	
	- In case of Monitoring is stopped then follow the instructions of `start monitoring-app` procedure described in [Monitoring application](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/BigStreamer/supportDocuments/procedures/manage-monitoring-app.md#procedure) doc

## Troubleshooting
- An email will be sent by the system with the point of failure.
- Check the log file for errors/exceptions  
	`egrep -i 'error|fail|exception|problem' /shared/abc/brond_dsl_stats/DataParser/scripts/log/002.Brond_xDSL_Load.YYYYMMDD.log`

- List Failed Monitoring messages of the last load
	```
	/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`

	select * from jobstatus where upper(job) like 'BROND__DSL' 
	and status='FAILED'
	and operative_partition=(select max(operative_partition) from jobstatus where upper(job) like 'BROND__DSL' and operative_partition regexp '[0-9]{8}')
	order by id
	;

	execution_id | id    | application | job              | component                                | operative_partition | status  | system_ts           | system_ts_end       | message                | user  | host                  
	-------------+-------+-------------+------------------+------------------------------------------+---------------------+---------+---------------------+---------------------+------------------------+-------+-----------------------
	1659946615   | 15825 | BROND       | BROND_ADSL_STATS | MAIN                                     | 20220808            | FAILED  | 2022-08-08 11:16:55 | 2022-08-08 11:16:55 | No raw files found     | brond | un2.bigdata.abc.gr
	1659946615   | 15827 | BROND       | BROND_ADSL_STATS | GET RAW XDSL FILES                       | 20220808            | FAILED  | 2022-08-08 11:16:55 |                     | No raw files found     | brond | un2.bigdata.abc.gr
	1659946615   | 15829 | BROND       | BROND_VDSL_STATS | MAIN                                     | 20220808            | FAILED  | 2022-08-08 11:16:56 | 2022-08-08 11:16:56 | No raw files found     | brond | un2.bigdata.abc.gr
	1659946615   | 15831 | BROND       | BROND_VDSL_STATS | GET RAW XDSL FILES                       | 20220808            | FAILED  | 2022-08-08 11:16:56 |                     | No raw files found     | brond | un2.bigdata.abc.gr
	```

### Common errors  
- `No raw files found`, there are no raw files available for loading at remdef server.  
A WARNING message will be sent to abc by email.
No actions required from OBSS. Responsible abc. 

- Other factors not related to the specific flow
	- impala/hive availability
	- Kerberos authentication (A.  
	*Ndef: The flow checks if the ticket is still active before any HDFS action.  
	In case of expiration the flow performs a `kinit` command*

## Manually triggering the workflow

There are cases where abc might upload new files after the scheduled workflow timing, and request these files to be
processed in the same day. This can only be done by manually triggering the workflow. Before doing so, you need to make some checks first:

### Check workflow logs

1. Login to https://999.999.999.999:8888/hue/accounts/login?next=/hue using the brond account
2. Go to "Jobs" > "Workflows"

If all workflow executions ("Brond_Load_xDSL_WF_NEW") were successful, you can proceed by checking that the file(s)
abc added, were copied after the scheduled timings of the workflow

### Check added files

sftp get raw files (*.csv.gz) from FTP Server to `/data/1/brond_retr_LZ`
```
echo "ls -l ADSL_Brond" | sftp bigd@999.999.999.999
sftp> ls -l ADSL_Brond
-rw-r--r-- 0 507 500 21925249 Nov 29 06:22 ADSL_Brond/Counter_Collection_24H.329_2022_11_29.csv.gz.LOADED
-rw-r--r-- 0 507 500 22107252 Nov 29 13:52 ADSL_Brond/Counter_Collection_24H.330_2022_11_29.csv.gz
```

The second file was indeed added after the scheduled time and has not been picked up by the workflow.

### Trigger workflow

You can now proceed to manually trigger the workflow:

1. Go to HUE and select "Jobs"
2. Go to "Workflow" and select "Brond_Load_xDSL_WF_NEW"
3. In the next screen, select "Rerun"
4. Wait for the workflow to successfully end
5. If no errors occur, proceed with:
sftp get raw files (*.csv.gz) from FTP Server to `/data/1/brond_retr_LZ`
```
echo "ls -l ADSL_Brond" | sftp bigd@999.999.999.999
sftp> ls -l ADSL_Brond
-rw-r--r-- 0 507 500 21925249 Nov 29 06:22 ADSL_Brond/Counter_Collection_24H.329_2022_11_29.csv.gz.LOADED
-rw-r--r-- 0 507 500 22107252 Nov 29 13:52 ADSL_Brond/Counter_Collection_24H.330_2022_11_29.csv.gz.LOADED
```

## Data Check
- **Check final tables for new partitions**:
  - Impala-shell: 
	```
	/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k

	refresh brond.brond_adsl_stats_daily;  
	show partitions brond.brond_adsl_stats_daily;  
	
	par_dt   | #Rows  | #Files | Size     | Bytes Cached | Cache Replication | Format | Incremental stats | Location                                                                        
	---------+--------+--------+----------+--------------+-------------------+--------+-------------------+---------------------------------------------------------------------------------
	20221130 | 629397 |      1 | 155.09MB | NOT CACHED   | NOT CACHED        | TEXT   | false             | hdfs://nameservice1/ez/warehouse/brond.db/brond_adsl_stats_daily/par_dt=20220808
	Total    |     -1 |      1 | 155.09MB | 0B           |                   |        |                   |                                                                                 


	refresh brond.brond_vdsl_stats_daily;
	show partitions brond.brond_vdsl_stats_daily
	
	par_dt   | #Rows   | #Files | Size     | Bytes Cached | Cache Replication | Format | Incremental stats | Location                                                                        
	---------+---------+--------+----------+--------------+-------------------+--------+-------------------+---------------------------------------------------------------------------------
	20221130 | 2157413 |      1 | 588.26MB | NOT CACHED   | NOT CACHED        | TEXT   | false             | hdfs://nameservice1/ez/warehouse/brond.db/brond_vdsl_stats_daily/par_dt=20220808
	Total    |      -1 |      1 | 588.26MB | 0B           |                   |        |                   |                                                                                 
	```

- **Check the amount of data in final tables**:
  - Impala-shell: 
	```
	/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k

	SELECT par_dt, count(*) as cnt from brond.brond_adsl_stats_daily group by par_dt order by 1;
	par_dt   | cnt   
	---------+-------
	20221130 | 629397

	SELECT par_dt, count(*) as cnt from brond.brond_vdsl_stats_daily group by par_dt order by 1;
	par_dt   | cnt    
	---------+--------
	20221130 | 2157413
	```
	
