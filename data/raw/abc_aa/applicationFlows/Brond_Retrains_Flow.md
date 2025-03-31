# Brond Retrains Flow

## Installation info

### Data Source File
- Source system: FTP Server  
  - host :`999.999.999.999`
  - port :`22`
  - protocol :`SFTP`
  - user : `bigd`
  - spool area : `/ADSL_Brond`
  - file_type : `Counter_Collection_24H.*.csv.gz`
  - load_suffix : `LOADED`

- Local FileSystem Directories
	- node : `un-vip.bigdata.abc.gr (999.999.999.999)`
	- landing_zone : `/data/1/brond_retr_LZ`
	- archive_dir : `/data/1/brond_retr_LZ/archives`
	- work_dir : `/shared/brond_retr_repo`

- HDFS Directories
	- hdfs_Bin : `/user/brond`
	- hdfs_dir : `/ez/warehouse/brond.db/landing_zone/brond_retrains`
	- hdfs_pending_dir : `/ez/warehouse/brond.db/landing_zone/brond_retrains/not_loaded`
	- hdfs_stats_dir : `/ez/warehouse/brond.db/landing_zone/brond_retrains/stats`

### Scripts-Configuration Location
- node : `un-vip.bigdata.abc.gr (999.999.999.999)`
- user : `brond`
- scripts path : `/shared/abc/brond/DataParser/scripts`
-	configurations path : `/shared/abc/brond/DataParser/scripts/transferlist/*.trn` (i.e. brond_retrains.trn)

### Logs Location
- node : `un-vip.bigdata.abc.gr (999.999.999.999)`
- user : `brond`
- path : `/shared/abc/brond/DataParser/scripts/log`
- log file: `002.Brond_Retrains_Load.<YYYYMMDD>.log`

### Oozie Scheduling
- user : `brond`
- Coordinator :`Brond_Load_Retrains_Coord_NEW`  
	runs at : `04:10, 05:10, 06:10, 10:10 UTC`
- Workflow : `Brond_Load_Retrains_WF_NEW`  
- Main script : `HDFS:/user/brond/000.Brond_Retrains_Oozie_Main.sh`
- SSH Identity file : `HDFS:/user/brond/id_rsa`

Ndef: **Main Script** runs `oozie_brond_retrains.sh` located on `un-vip.bigdata.abc.gr` using **ssh** as user **brond**  
`$ ssh -o "StrictHostKeyChecking no" -i ./id_rsa brond@un-vip.bigdata.abc.gr "/shared/abc/brond/DataParser/scripts/oozie_brond_retrains.sh"`

### Hive Tables
- Target Database: `brond`
- Target Tables: `brond.brond_retrains_hist`

### Beeline-Impala Shell commands
- Beeline: `/usr/bin/beeline -u "jdbc:hive2://un-vip.bigdata.abc.gr:10000/default;principal=hive/_HOST@CNE.abc.GR;ssl=true;sslTrustStore=/usr/java/latest/jre/lib/security/jssecacerts;trustStorePassword=changeit"`
- Impala-shell: `/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k`

## Data process

1. sftp get raw files (*.csv.gz) from FTP Server to `/data/1/brond_retr_LZ`
```
echo "ls -l ADSL_Brond" | sftp bigd@999.999.999.999

sftp> ls -l ADSL_Brond
-rw-r--r-- 0 507 500 21902115 Nov 28 07:02 ADSL_Brond/Counter_Collection_24H.328_2022_11_28.csv.gz.LOADED
-rw-r--r-- 0 507 500 21925249 Nov 29 06:22 ADSL_Brond/Counter_Collection_24H.329_2022_11_29.csv.gz.LOADED
-rw-r--r-- 0 507 500 22107252 Nov 30 06:52 ADSL_Brond/Counter_Collection_24H.330_2022_11_30.csv.gz
```
2. rename the raw file(s) in remdef SFTP server by adding the suffix .LOADED
	`echo "rename /ADSL_Brond/Counter_Collection_24H.330_2022_11_30.csv.gz /ADSL_Brond/Counter_Collection_24H.330_2022_11_30.csv.gz.LOADED" | sftp -oport=22 bigd@999.999.999.999`
3. unzip raw files using `gzip -d` command in `/data/1/brond_retr_LZ`
4. parsing raw files in `/data/1/brond_retr_LZ`
	- removes the headers (1st line)
	- removes double-qudefs chars
	- defines the PAR_DT value from the filename (i.e. Counter_Collection_24H.330_2022_11_30.csv.gz convert to 20221130)
	- add the prefix `RETR___` to raw file
	- add the suffix `<load time>.parsed` to raw file  
		Load time format:`<YYYYMMDD_HHMISS>`  
		i.e. `RETR___Counter_Collection_24H.330_2022_11_30.csv.20221201_061005.parsed`
		
5. put raw files into HDFS landingzone
	`hdfs dfs -put /data/1/brond_retr_LZ/RETR___Counter_Collection_24H.330_2022_11_30.csv.20221201_061005.parsed /ez/warehouse/brond.db/landing_zone/brond_retrains/RETR___Counter_Collection_24H.330_2022_11_30.csv.20221201_061005.parsed`
6. clean-up any copy of the raw files from local filesystem  
	`/data/1/brond_retr_LZ`  
	`/shared/brond_retr_repo`  
7. load HDFS files into hive table `brond.brond_retrains_hist`
	`beeline -e "LOAD DATA INPATH '/ez/warehouse/brond.db/landing_zone/brond_retrains/RETR___Counter_Collection_24H.330_2022_11_30.csv.20221201_061005.parsed' OVERWRITE INTO TABLE brond.brond_retrains_hist PARTITION (par_dt='20221130')"`

8. execute compute stats using impala-shell  
	```
	/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k
	
	compute incremental stats brond.brond_retrains_hist;
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
For each load the following set of messages will be recorded in the Monitoring database.
```
id    | execution_id | application | job            | component                        | operative_partition | status  | system_ts           | system_ts_end       | message                | user  | host                  
------+--------------+-------------+----------------+----------------------------------+---------------------+---------+---------------------+---------------------+------------------------+-------+-----------------------
15807 | 1659939004   | BROND       | BROND_RETRAINS | MAIN                             | 20220808            | SUCCESS | 2022-08-08 09:10:04 | 2022-08-08 09:10:48 | Succesfully Completed. | brond | un2.bigdata.abc.gr
15809 | 1659939004   | BROND       | BROND_RETRAINS | GET_RAW_RETRAIN_FILES            | 20220808            | SUCCESS | 2022-08-08 09:10:05 |                     | Single raw file found  | brond | un2.bigdata.abc.gr
15811 | 1659939004   | BROND       | BROND_RETRAINS | RENAME_FILES_@SFTP_SERVER        | 20220808            | SUCCESS | 2022-08-08 09:10:05 |                     |                        | brond | un2.bigdata.abc.gr
15813 | 1659939004   | BROND       | BROND_RETRAINS | UNZIP_FILES                      | 20220808            | SUCCESS | 2022-08-08 09:10:07 |                     |                        | brond | un2.bigdata.abc.gr
15815 | 1659939004   | BROND       | BROND_RETRAINS | PARSING_FILES                    | 20220808            | SUCCESS | 2022-08-08 09:10:13 |                     |                        | brond | un2.bigdata.abc.gr
15817 | 1659939004   | BROND       | BROND_RETRAINS | LOAD_HDFS_LANDINGZONE            | 20220808            | SUCCESS | 2022-08-08 09:10:26 |                     |                        | brond | un2.bigdata.abc.gr
15819 | 1659939004   | BROND       | BROND_RETRAINS | CLEAN-UP_THE_INPUT_FILES         | 20220808            | SUCCESS | 2022-08-08 09:10:26 |                     |                        | brond | un2.bigdata.abc.gr
15821 | 1659939004   | BROND       | BROND_RETRAINS | LOAD_HDFS_FILES_INTO_HIVE_TABLES | 20220808            | SUCCESS | 2022-08-08 09:10:37 |                     |                        | brond | un2.bigdata.abc.gr
15823 | 1659939004   | BROND       | BROND_RETRAINS | POST_SCRIPT                      | 20220808            | SUCCESS | 2022-08-08 09:10:48 |                     |                        | brond | un2.bigdata.abc.gr
```

### Monitoring Component list
|Component | Description 
|-|-|
|MAIN|Indicates the status of the whole load. <br />Status:RUNNING, SUCCESS, FAILED| 
|GET_RAW_RETRAIN_FILES|sftp-get the raw files from the remdef server.<br />i.e.<br />Counter_Collection_24H.218_2022_08_08.csv.gz
|RENAME_FILES_@SFTP_SERVER| Rename the raw files in remdef SFTP server by adding the suffix .LOADED<br />i.e.<br />Counter_Collection_24H.218_2022_08_08.csv.gz.LOADED
|UNZIP_FILES| unzip the raw files using `gzip -d` command
|PARSING_FILES| removes any control chars (if any) from the raw files
|LOAD_HDFS_LANDINGZONE|PUT the parsing files into HDFS landingzone `/ez/warehouse/brond.db/landing_zone/brond_retrains`
|CLEAN-UP_THE_INPUT_FILES|Clean-up any copy of the raw files from the filesystem (`/data/1/brond_retr_LZ`, `/shared/brond_retr_repo`)
|LOAD_HDFS_FILES_INTO_HIVE_TABLE| Load raw data (files) into the tables<br />`brond.brond_retrains_hist`
|POST_SCRIPT| Execute Compute Statistics using impala-shell.<br />`compute incremental stats brond.brond_retrains_hist;`

### Monitoring database Queries
- List messages of the last load  
	`/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`

	```
	select 
		execution_id, id, application, job, component, operative_partition,  
		status, system_ts, system_ts_end, message, user,host   
	from jobstatus a where upper(job) like 'BROND_RETRAINS%'   
	and execution_id=(select max(execution_id) from jobstatus where upper(job) like 'BROND_RETRAINS%')  
	;

	execution_id | id    | application | job            | component                        | operative_partition | status  | system_ts           | system_ts_end       | message                | user  | host                  
	-------------+-------+-------------+----------------+----------------------------------+---------------------+---------+---------------------+---------------------+------------------------+-------+-----------------------
	1659939004   | 15807 | BROND       | BROND_RETRAINS | MAIN                             | 20220808            | SUCCESS | 2022-08-08 09:10:04 | 2022-08-08 09:10:48 | Succesfully Completed. | brond | un2.bigdata.abc.gr
	1659939004   | 15809 | BROND       | BROND_RETRAINS | GET RAW RETRAIN FILES            | 20220808            | SUCCESS | 2022-08-08 09:10:05 |                     | Single raw file found  | brond | un2.bigdata.abc.gr
	1659939004   | 15811 | BROND       | BROND_RETRAINS | RENAME FILES @SFTP SERVER        | 20220808            | SUCCESS | 2022-08-08 09:10:05 |                     |                        | brond | un2.bigdata.abc.gr
	1659939004   | 15813 | BROND       | BROND_RETRAINS | UNZIP FILES                      | 20220808            | SUCCESS | 2022-08-08 09:10:07 |                     |                        | brond | un2.bigdata.abc.gr
	1659939004   | 15815 | BROND       | BROND_RETRAINS | PARSING FILES                    | 20220808            | SUCCESS | 2022-08-08 09:10:13 |                     |                        | brond | un2.bigdata.abc.gr
	1659939004   | 15817 | BROND       | BROND_RETRAINS | LOAD HDFS LANDINGZONE            | 20220808            | SUCCESS | 2022-08-08 09:10:26 |                     |                        | brond | un2.bigdata.abc.gr
	1659939004   | 15819 | BROND       | BROND_RETRAINS | CLEAN-UP THE INPUT FILES         | 20220808            | SUCCESS | 2022-08-08 09:10:26 |                     |                        | brond | un2.bigdata.abc.gr
	1659939004   | 15821 | BROND       | BROND_RETRAINS | LOAD HDFS FILES INTO HIVE TABLES | 20220808            | SUCCESS | 2022-08-08 09:10:37 |                     |                        | brond | un2.bigdata.abc.gr
	1659939004   | 15823 | BROND       | BROND_RETRAINS | POST SCRIPT                      | 20220808            | SUCCESS | 2022-08-08 09:10:48 |                     |                        | brond | un2.bigdata.abc.gr
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
	`egrep -i 'error|fail|exception|problem' /shared/abc/brond/DataParser/scripts/log/002.Brond_Retrains_Load.<YYYYMMDD>.log`

- List Failed Monitoring messages of the last load  
	```
	/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`

	select * from jobstatus where upper(job) like 'BROND_RETRAINS%' 
	and status='FAILED'
	and operative_partition=(select max(operative_partition) from jobstatus where upper(job) like 'BROND_RETRAINS%' and operative_partition regexp '[0-9]{8}')
	order by id
	;

	id    | execution_id | application | job            | component             | operative_partition | status | system_ts           | system_ts_end       | message            | user  | host                  
	------+--------------+-------------+----------------+-----------------------+---------------------+--------+---------------------+---------------------+--------------------+-------+-----------------------
	14621 |              | BROND       | BROND_RETRAINS | MAIN                  | 20220801            | FAILED | 2022-08-01 16:13:13 | 2022-08-01 16:13:14 | No raw files found | brond | un2.bigdata.abc.gr
	14623 |              | BROND       | BROND_RETRAINS | GET RAW RETRAIN FILES | 20220801            | FAILED | 2022-08-01 16:13:14 |                     | No raw files found | brond | un2.bigdata.abc.gr
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

If all workflow executions ("Brond_Load_Retrains_WF_NEW") were successful, you can proceed by checking that the file(s)
abc added, were copied after the scheduled timings of the workflow

### Check added files

sftp get raw files (*.csv.gz) from FTP Server to `/data/1/brond_dsl_stats_LZ`
```
echo "ls -l ADSL_Brond_DWH" | sftp bigd@999.999.999.999
sftp> ls -l ADSL_Brond_DWH
-rw-r--r--    0 507      500      150589497 Nov 29 05:34 ADSL_Brond_DWH/DWH_VDSL.329_2022_11_29.csv.gz.LOADED
-rw-r--r--    0 507      500      150823890 Nov 29 13:21 ADSL_Brond_DWH/DWH_VDSL.330_2022_11_29.csv.gz
```

The second file was indeed added after the scheduled time and has not been picked up by the workflow.

### Trigger workflow

You can now proceed to manually trigger the workflow:

1. Go to HUE and select "Jobs"
2. Go to "Workflow" and select "Brond_Load_Retrains_WF_NEW"
3. In the next screen, select "Rerun"
4. Wait for the workflow to successfully end
5. If no errors occur, proceed with:
sftp get raw files (*.csv.gz) from FTP Server to `/data/1/brond_dsl_stats_LZ`
```
echo "ls -l ADSL_Brond_DWH" | sftp bigd@999.999.999.999
sftp> ls -l ADSL_Brond_DWH
-rw-r--r--    0 507      500      150589497 Nov 29 05:34 ADSL_Brond_DWH/DWH_VDSL.329_2022_11_29.csv.gz.LOADED
-rw-r--r--    0 507      500      150823890 Nov 29 13:21 ADSL_Brond_DWH/DWH_VDSL.330_2022_11_29.csv.gz
```

## Data Check
- **Check final tables for new partitions**:
  - Impala-shell: 
	```
	/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k

	refresh brond.brond_retrains_hist;  
	show partitions brond.brond_retrains_hist;  
	
	par_dt   | #Rows   | #Files | Size     | Bytes Cached | Cache Replication | Format | Incremental stats | Location                                                                     
	---------+---------+--------+----------+--------------+-------------------+--------+-------------------+------------------------------------------------------------------------------
	20221130 | 2784494 |      1 | 146.16MB | NOT CACHED   | NOT CACHED        | TEXT   | true              | hdfs://nameservice1/ez/warehouse/brond.db/brond_retrains_hist/par_dt=20221130
	Total    | 5569421 |      1 | 146.16MB | 0B           |                   |        |                   |                                                                              
	```

- **Check the amount of data in final tables**:
  - Impala-shell: 
	```
	/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k

	select par_dt, count(*) as cnt from brond.brond_retrains_hist group by par_dt order by 1;
	
	par_dt   | cnt    
	---------+--------
	20221130 | 2784494
	```
	
