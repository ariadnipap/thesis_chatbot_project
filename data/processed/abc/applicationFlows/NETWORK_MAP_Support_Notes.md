---
title: def_NETWORK_MAP ETL Flow (OneTicket)
system: BigStreamer
component: OneTicket
job_name: Oracle_to_Hive_OneTicket_Load
source_system: Oracle
source_tables:
  - def_NETWORK_MAP.ACTIVITY
  - def_NETWORK_MAP.AFFECTED_CUSTOMERS
  - def_NETWORK_MAP.AFFECTED_OCT_WTT
  - def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT
  - def_NETWORK_MAP.OPEN_MW
  - def_NETWORK_MAP.OPEN_NTT
  - def_NETWORK_MAP.OPEN_OCT
  - def_NETWORK_MAP.OPEN_WTT
destination_system: Hive
destination_tables:
  - def_network_map.activity
  - def_network_map.affected_customers
  - def_network_map.affected_oct_wtt
  - def_network_map.defective_netw_element
  - def_network_map.open_mw
  - def_network_map.open_ntt
  - def_network_map.open_oct
  - def_network_map.open_wtt
schedule: every 5 minutes
coordinator: def_NETWORK_MAP_Coordinator
workflow: def_NETWORK_MAP_Workflow
script_path: HDFS:/user/def_network_maps/100.OneTicket_Main.sh
monitoring_table: monitoring.jobstatus
owner: def_network_maps
tags:
  - OneTicket
  - Oracle to Hive ETL
  - def_NETWORK_MAP
  - BigStreamer
  - Monitoring
  - Oozie
  - HDFS
  - Impala
  - Beeline
  - Troubleshooting
  - Log Analysis
---
# def_NETWORK_MAP Flow (OneTicket)
This document describes the ETL process that exports operational data from Oracle to Hive every 5 minutes using the OneTicket flow. It covers installation details, process phases, monitoring mechanisms, and troubleshooting steps. The data is primarily used for network defect tracking and service impact analysis.
## Installation & Setup
Configuration paths, database sources, and execution environment for the OneTicket ETL process.
### Data Source Tables
- Source system: Oracle Database 11g Enterprise Edition (999.999.999.999.0)  
	- Server:`999.999.999.999:1521`
	- Port Forward:`999.999.999.999:1521`
	- User:`def_network_map`
	- SID:`defsblf_rw`
	- Oracle Tables: 
		- def_NETWORK_MAP.ACTIVITY
		- def_NETWORK_MAP.AFFECTED_CUSTOMERS
		- def_NETWORK_MAP.AFFECTED_OCT_WTT
		- def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT
		- def_NETWORK_MAP.OPEN_MW
		- def_NETWORK_MAP.OPEN_NTT
		- def_NETWORK_MAP.OPEN_OCT
		- def_NETWORK_MAP.OPEN_WTT
		- def_NETWORK_MAP.EXPORT_CTL
### Scripts-Configuration Location in HDFS
- user : `def_network_maps`
- scripts path : `HDFS:/user/def_network_maps/`
-	configuration path : `HDFS:/user/def_network_maps/`
	- `oneTicket_env.sh`, The environment of the flow
	- `OraExpData.tables`, List of tables which are going to be exported/imported from Oracle to Hive
	- `monitoring.config`, The `Monitoring` connection details
	- `oraclecmd.config`, The Oracle connection details
	- `oneticket.keystore`, The Oracle password file
- Temp dir : `HDFS:/ez/landingzone/tmp/oneTicket`
### Export Data Location
- node : Dynamically defined by the Oozie service  
	i.e. `sn95.bigdata.abc.gr`
- Directory : Dynamically defined by the Oozie service
	i.e. `/data/2/yarn/nm/usercache/def_network_maps/appcache/application_1668434520231_277391/container_e276_1668434520231_277391_01_000001`
### Logs Location
- user : `def_network_maps`
- logs path : `/user/def_network_maps/log`
- log files: 
	- `101.OneTicket_OraMetaData.<YYYYMM>.log`
	- `102.OneTicket_OraData_CTRL.<YYYYMM>.log`
	- `103.OneTicket_OraData_Export_Import.<TABLE_NAME>.<UNIX-TIME>.log`
	- `104.OneTicket_OraData_Import_Hive.<UNIX-TIME>.log`
	`<UNIX-TIME>` is the timestamp of the load in unix-epoch format  
	`<TABLE_NAME>` list of values:  
	- def_NETWORK_MAP.ACTIVITY
	- def_NETWORK_MAP.AFFECTED_CUSTOMERS
	- def_NETWORK_MAP.AFFECTED_OCT_WTT
	- def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT
	- def_NETWORK_MAP.OPEN_MW
	- def_NETWORK_MAP.OPEN_NTT
	- def_NETWORK_MAP.OPEN_OCT
	- def_NETWORK_MAP.OPEN_WTT
	i.e.  
	```
	$ hdfs dfs -ls -t -r /user/def_network_maps/log
	
	101.OneTicket_OraMetaData.202302.log
	102.OneTicket_OraData_CTRL.202302.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.ACTIVITY.1675939511.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.AFFECTED_CUSTOMERS.1675939511.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.AFFECTED_OCT_WTT.1675939511.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT.1675939511.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.OPEN_MW.1675939511.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.OPEN_NTT.1675939511.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.OPEN_OCT.1675939511.log
	103.OneTicket_OraData_Export_Import.def_NETWORK_MAP.OPEN_WTT.1675939511.log
	104.OneTicket_OraData_Import_Hive.1675939511.log	
	```
### Oozie Scheduling
- user : def_network_maps
- Coordinator :`def_NETWORK_MAP_Coordinator`  
	runs at : every 5 minutes on a Daily basis  
		`0,5,10,15,20,25,30,35,40,45,50,55 * * * *` 
- Workflow : `def_NETWORK_MAP_Workflow`  
	Bash script : `HDFS:/user/def_network_maps/100.OneTicket_Main.sh`
### Hive Tables
- Target Database: `def_network_map`
- Target Tables: 
	- def_NETWORK_MAP.ACTIVITY
	- def_NETWORK_MAP.AFFECTED_CUSTOMERS
	- def_NETWORK_MAP.AFFECTED_OCT_WTT
	- def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT
	- def_NETWORK_MAP.OPEN_MW
	- def_NETWORK_MAP.OPEN_NTT
	- def_NETWORK_MAP.OPEN_OCT
	- def_NETWORK_MAP.OPEN_WTT
### Database CLI commands
- Beeline: `/usr/bin/beeline -u "jdbc:hive2://un-vip.bigdata.abc.gr:10000/def_network_map;principal=hive/_HOST@CNE.abc.GR;ssl=true;sslTrustStore=/usr/java/latest/jre/lib/security/jssecacerts;trustStorePassword=changeit"`
- Impala: `/usr/bin/impala-shell -i un-vip.bigdata.abc.gr -d def_network_map --ssl -k`
- Oracle*: `sqlplus -s def_network_map/<PASSWORD>@999.999.999.999:1521/defsblf_rw`
- MySql*: `mysql -u monitoring -p -h 999.999.999.999 monitoring`
*\*The passwords for the Oracle and MySql databases can be found [here](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/devpasswd.kdbx)*
## Data Process: Oracle to Hive ETL Steps
Step-by-step breakdown of how data is exported from Oracle and ingested into Hive tables.
### In General
The flow consist of two basic procedures and one control Oracle table.  
	- the **Export** procedure, which is running at the remdef Oracle server (Responsible def/abc),  
	- the **Import** procedure, which is running at the BigStreamer cluster,  
	- the `def_NETWORK_MAP.EXPORT_CTL` table, used to synchronize the **Export** procedure with the **Import** procedure.  
The data in `def_NETWORK_MAP.EXPORT_CTL` is similar to the following
Connect to Oracle (see [Database CLI commands](#database-cli-commands))  
```
select * from def_NETWORK_MAP.EXPORT_CTL;  
EXPORT_SEQUENCE | TARGET                 | EXPORT_START_DT     | EXPORT_END_DT       | ROW_COUNT | IMPORT_START_DT     | IMPORT_END_DT      
----------------+------------------------+---------------------+---------------------+-----------+---------------------+--------------------
              0 | TOTAL                  | 2022-11-15 16:50:01 | 2022-11-15 17:07:09 |           | 2022-11-22 09:28:24 | 2022-11-22 09:29:12
              5 | ACTIVITY               | 2022-11-15 16:51:27 | 2022-11-15 17:04:36 |     73211 |                     |                    
              6 | AFFECTED_CUSTOMERS     | 2022-11-15 17:04:36 | 2022-11-15 17:04:54 |     14438 |                     |                    
              7 | OPEN_OCT               | 2022-11-15 17:04:54 | 2022-11-15 17:07:05 |     58338 |                     |                    
              8 | OPEN_WTT               | 2022-11-15 17:07:05 | 2022-11-15 17:07:09 |      3690 |                     |                    
              1 | OPEN_MW                | 2022-11-15 17:10:05 | 2022-11-15 17:10:42 |       249 |                     |                    
              2 | OPEN_NTT               | 2022-11-15 17:10:42 | 2022-11-15 17:11:03 |      6957 |                     |                    
              3 | AFFECTED_OCT_WTT       | 2022-11-15 17:11:03 | 2022-11-15 17:11:20 |      1782 |                     |                    
              4 | DEFECTIVE_NETW_ELEMENT | 2022-11-15 17:11:20 | 2022-11-15 17:11:21 |      6236 |                     |                    
```
  Ndef: We are interesting for the 1st row only `EXPORT_SEQUENCE=0`  
### Phased
1. The **Export** procedure is implemented by def/abc.  
	It is responsible to prepare the data in Oracle tables (see Oracle Table list in [Data Source Tables](#data-source-tables))  
	Once completed, it updates the `def_NETWORK_MAP.EXPORT_CTL.EXPORT_START_DT` column with the current system's timestamp.   
	Ndef: It is not known how often the **Export** procedure runs.
2.  The **Import** procedure is implemented by jkl.  
	It checks periodically if the value of `def_NETWORK_MAP.EXPORT_CTL.EXPORT_START_DT` has been updated.  
	- In case of new value, the procedure exports the data from the Oracle tables  
	`./oracle_cmd.sh "select * from <table>" > ./<table>.exp`  
	- stores them into HDFS  
	`hdfs dfs -moveFromLocal ./<table>.exp .`
	- and, consequently, load them into the corresponding [Hive Tables](#hive-tables).  
	*Connect to Beeline (see [Database CLI commands](#database-cli-commands))*
	`Beeline <connection> -e "load data inpath './<table>.exp' overwrite into table <table>;"`
	- Once the Import procedure completed, the `IMPORT_START_DT` column will be updated with the current system's timestamp.   
	*Connect to Oracle (see [Database CLI commands](#database-cli-commands))*
	`update def_NETWORK_MAP.EXPORT_CTL.EXPORT_START_DT`
	- Compute table statistics using impala-shell	 
	*Connect to Impala (see [Database CLI commands](#database-cli-commands))*
	`compute incremental stats brond.brond_retrains_hist;`
3. In case the `EXPORT_START_DT` value isn't updated, the **Import** procedure exists doing nothing.
## Monitoring
Describes how load jobs are tracked in the monitoring.jobstatus table and validated via logs and queries.
### Monitoring connection details
|Field|Value|
|-|-|
|Database Type| mysql  
|Host| 999.999.999.999  
|DB Name| monitoring  
|DB User| monitoring  
|Table| jobstatus  
Connection command: `/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`
### Monitoring Message list → Monitoring Messages in MySQL
For each load for each TABLE the following set of messages will be recorded in the Monitoring database.
```sql
execution_id | id     | application | job             | component                 | operative_partition | status  | system_ts           | system_ts_end       | param0 | message                                                              | user             | host                    
-------------+--------+-------------+-----------------+---------------------------+---------------------+---------+---------------------+---------------------+--------+----------------------------------------------------------------------+------------------+-------------------------
1670509202   | 402171 | ONETICKET   | def_NETWORK_MAP | MAIN                      | 20221208_1620       | SUCCESS | 2022-12-08 16:20:02 | 2022-12-08 16:22:05 |        | Procedure Started                                                    | def_network_maps | un-vip.bigdata.abc.gr
1670509202   | 402173 | ONETICKET   | def_NETWORK_MAP | CHECK_FOR_AVAILABLE_DATA  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:02 |                     |        | New data found: 2022-12-08 15:50:04                                  | def_network_maps | un-vip.bigdata.abc.gr
1670509202   | 402207 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-<TABLE-NAME>  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:24 |                     | 6987   | Oracle export def_NETWORK_MAP.OPEN_NTT data. Rows:6987               | def_network_maps | un-vip.bigdata.abc.gr
1670509202   | 402209 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-<TABLE-NAME> | 20221208_1620       | SUCCESS | 2022-12-08 16:20:24 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
1670509202   | 402211 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-<TABLE-NAME>    | 20221208_1620       | SUCCESS | 2022-12-08 16:20:27 |                     |        | Move def_NETWORK_MAP.OPEN_NTT data in HDFS                           | def_network_maps | un-vip.bigdata.abc.gr
1670509202   | 402241 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-<TABLE-NAME>    | 20221208_1620       | SUCCESS | 2022-12-08 16:21:32 |                     |        | Load def_NETWORK_MAP.OPEN_NTT data into Hive                         | def_network_maps | un-vip.bigdata.abc.gr
1670509202   | 402247 | ONETICKET   | def_NETWORK_MAP | COMPUTE_STATS             | 20221208_1620       | SUCCESS | 2022-12-08 16:22:04 |                     |        | Compute statistics                                                   | def_network_maps | un-vip.bigdata.abc.gr
```
### Monitoring Component list
|Component | Description 
|-|-|
|MAIN|Indicates the status of the whole load. <br />Status:RUNNING, SUCCESS, FAILED| 
|CHECK_FOR_AVAILABLE_DATA| Check the Oracle table EXPORT_CTL if there are new data to export
|EXPORT_DATA-\<TABLE-NAME\>| Exports data from Oracle to `/shared/abc/oneTicket/exp`
|DATA_PARSING-\<TABLE-NAME\>| Change column separator and remove the string "null"
|HDFS_MOVE-\<TABLE-NAME\>| Move export file from local file system to HDFS `/ez/landingzone/tmp/oneTicket`
|LOAD_DATA-\<TABLE-NAME\>| Load export file from HDFS `/ez/landingzone/tmp/oneTicket` into the HIVE table (i.e. `def_NETWORK_MAP.OPEN_NTT`)
|COMPUTE_STATS| performs compute statistics on HIVE tables using impala-shell
### Monitoring database Queries → Sample Monitoring DB Queries
- List messages of the last load  
`/usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring`
```sql
  select 
    execution_id, id, application, job, component, operative_partition,  
    status, system_ts, system_ts_end, param0, message, user,  host
  from jobstatus a where 1=1
  and upper(application)='ONETICKET' and upper(job) like 'def_NETWORK_MAP'   
  and execution_id=(
    select max(execution_id) execution_id from jobstatus where 1=1
    and upper(application)='ONETICKET' and upper(job) like 'def_NETWORK_MAP'   
    and lower(message) not like '%no new export found%' 
    and component='CHECK_FOR_AVAILABLE_DATA'
    and system_ts>=date(now())-30)
  order by id
  ;

  execution_id | id     | application | job             | component                                           | operative_partition | status  | system_ts           | system_ts_end       | param0 | message                                                              | user             | host                    
  -------------+--------+-------------+-----------------+-----------------------------------------------------+---------------------+---------+---------------------+---------------------+--------+----------------------------------------------------------------------+------------------+-------------------------
  1670509202   | 402171 | ONETICKET   | def_NETWORK_MAP | MAIN                                                | 20221208_1620       | SUCCESS | 2022-12-08 16:20:02 | 2022-12-08 16:22:05 |        | Procedure Started                                                    | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402173 | ONETICKET   | def_NETWORK_MAP | CHECK_FOR_AVAILABLE_DATA                            | 20221208_1620       | SUCCESS | 2022-12-08 16:20:02 |                     |        | New data found: 2022-12-08 15:50:04                                  | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402183 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.AFFECTED_OCT_WTT        | 20221208_1620       | SUCCESS | 2022-12-08 16:20:12 |                     | 1867   | Oracle export def_NETWORK_MAP.AFFECTED_OCT_WTT data. Rows:1867       | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402185 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.AFFECTED_OCT_WTT       | 20221208_1620       | SUCCESS | 2022-12-08 16:20:12 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402187 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.AFFECTED_CUSTOMERS      | 20221208_1620       | SUCCESS | 2022-12-08 16:20:15 |                     | 17397  | Oracle export def_NETWORK_MAP.AFFECTED_CUSTOMERS data. Rows:17397    | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402189 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.AFFECTED_OCT_WTT          | 20221208_1620       | SUCCESS | 2022-12-08 16:20:15 |                     |        | Move def_NETWORK_MAP.AFFECTED_OCT_WTT data in HDFS                   | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402191 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.AFFECTED_CUSTOMERS     | 20221208_1620       | SUCCESS | 2022-12-08 16:20:15 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402193 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.OPEN_MW                 | 20221208_1620       | SUCCESS | 2022-12-08 16:20:17 |                     | 238    | Oracle export def_NETWORK_MAP.OPEN_MW data. Rows:238                 | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402195 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.OPEN_MW                | 20221208_1620       | SUCCESS | 2022-12-08 16:20:17 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402197 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:18 |                     | 6035   | Oracle export def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT data. Rows:6035 | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402199 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT | 20221208_1620       | SUCCESS | 2022-12-08 16:20:18 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402201 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.AFFECTED_CUSTOMERS        | 20221208_1620       | SUCCESS | 2022-12-08 16:20:18 |                     |        | Move def_NETWORK_MAP.AFFECTED_CUSTOMERS data in HDFS                 | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402203 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.OPEN_MW                   | 20221208_1620       | SUCCESS | 2022-12-08 16:20:21 |                     |        | Move def_NETWORK_MAP.OPEN_MW data in HDFS                            | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402205 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT    | 20221208_1620       | SUCCESS | 2022-12-08 16:20:21 |                     |        | Move def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT data in HDFS             | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402207 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.OPEN_NTT                | 20221208_1620       | SUCCESS | 2022-12-08 16:20:24 |                     | 6987   | Oracle export def_NETWORK_MAP.OPEN_NTT data. Rows:6987               | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402209 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.OPEN_NTT               | 20221208_1620       | SUCCESS | 2022-12-08 16:20:24 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402211 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.OPEN_NTT                  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:27 |                     |        | Move def_NETWORK_MAP.OPEN_NTT data in HDFS                           | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402213 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.OPEN_WTT                | 20221208_1620       | SUCCESS | 2022-12-08 16:20:27 |                     | 3621   | Oracle export def_NETWORK_MAP.OPEN_WTT data. Rows:3621               | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402215 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.OPEN_WTT               | 20221208_1620       | SUCCESS | 2022-12-08 16:20:27 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402217 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.OPEN_WTT                  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:30 |                     |        | Move def_NETWORK_MAP.OPEN_WTT data in HDFS                           | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402219 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.ACTIVITY                | 20221208_1620       | SUCCESS | 2022-12-08 16:20:36 |                     | 74433  | Oracle export def_NETWORK_MAP.ACTIVITY data. Rows:74433              | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402221 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.ACTIVITY               | 20221208_1620       | SUCCESS | 2022-12-08 16:20:37 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402223 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.ACTIVITY                  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:40 |                     |        | Move def_NETWORK_MAP.ACTIVITY data in HDFS                           | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402225 | ONETICKET   | def_NETWORK_MAP | EXPORT_DATA-def_NETWORK_MAP.OPEN_OCT                | 20221208_1620       | SUCCESS | 2022-12-08 16:20:40 |                     | 60164  | Oracle export def_NETWORK_MAP.OPEN_OCT data. Rows:60164              | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402227 | ONETICKET   | def_NETWORK_MAP | DATA_PARSING-def_NETWORK_MAP.OPEN_OCT               | 20221208_1620       | SUCCESS | 2022-12-08 16:20:40 |                     |        | Change separator                                                     | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402229 | ONETICKET   | def_NETWORK_MAP | HDFS_MOVE-def_NETWORK_MAP.OPEN_OCT                  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:43 |                     |        | Move def_NETWORK_MAP.OPEN_OCT data in HDFS                           | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402231 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.ACTIVITY                  | 20221208_1620       | SUCCESS | 2022-12-08 16:20:57 |                     |        | Load def_NETWORK_MAP.ACTIVITY data into Hive                         | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402233 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.AFFECTED_CUSTOMERS        | 20221208_1620       | SUCCESS | 2022-12-08 16:21:04 |                     |        | Load def_NETWORK_MAP.AFFECTED_CUSTOMERS data into Hive               | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402235 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.AFFECTED_OCT_WTT          | 20221208_1620       | SUCCESS | 2022-12-08 16:21:11 |                     |        | Load def_NETWORK_MAP.AFFECTED_OCT_WTT data into Hive                 | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402237 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT    | 20221208_1620       | SUCCESS | 2022-12-08 16:21:18 |                     |        | Load def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT data into Hive           | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402239 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.OPEN_MW                   | 20221208_1620       | SUCCESS | 2022-12-08 16:21:25 |                     |        | Load def_NETWORK_MAP.OPEN_MW data into Hive                          | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402241 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.OPEN_NTT                  | 20221208_1620       | SUCCESS | 2022-12-08 16:21:32 |                     |        | Load def_NETWORK_MAP.OPEN_NTT data into Hive                         | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402243 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.OPEN_OCT                  | 20221208_1620       | SUCCESS | 2022-12-08 16:21:39 |                     |        | Load def_NETWORK_MAP.OPEN_OCT data into Hive                         | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402245 | ONETICKET   | def_NETWORK_MAP | LOAD_DATA-def_NETWORK_MAP.OPEN_WTT                  | 20221208_1620       | SUCCESS | 2022-12-08 16:21:46 |                     |        | Load def_NETWORK_MAP.OPEN_WTT data into Hive                         | def_network_maps | un-vip.bigdata.abc.gr
  1670509202   | 402247 | ONETICKET   | def_NETWORK_MAP | COMPUTE_STATS                                       | 20221208_1620       | SUCCESS | 2022-12-08 16:22:04 |                     |        | Compute statistics                                                   | def_network_maps | un-vip.bigdata.abc.gr
  ```
### Monitoring Health-Check
- Check Monitoring status.  
```bash  
$ curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/app/check'  
{"code":0,"info":"App is up and running. Current time:20220803 06:46:57.708 +0000"}
```
- In case of Monitoring is stopped then follow the instructions of `start monitoring-app` procedure described in [Monitoring application](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/BigStreamer/supportDocuments/procedures/manage-monitoring-app.md#procedure) doc
## Troubleshooting
Actions to follow in case of failure, based on alert messages and log investigation.
An email will be sent by the system with the point of failure.  
i.e.
<pre>
From: abc_bigd@abc.gr  
Subject: ONETICKET - def_NETWORK_MAP: FAILED  
Load <b>def_NETWORK_MAP.ACTIVITY</b> data into Hive (1673849411)  
<b>Exec_id:1673849411</b>  
This is an automated e-mail.  
Please do not reply.  
</pre>
**Actions**  
1. Write down the values of the `Table name` and `Exec_id` described in the alert email  
i.e. 
- Table name: `def_NETWORK_MAP.ACTIVITY`
- Exec_id:`1673849411`
2. Copy from HDFS the folowing log files which contains the specific `Table name` and `Exec_id` in its filename.
- 103.OneTicket_OraData_Export_Import.\<Table name\>.\<Exec_id\>.log
- 104.OneTicket_OraData_Import_Hive.\<Exec_id\>.log
<pre>
hdfs dfs -get /user/def_network_maps/hdfs dfs -get 103.OneTicket_OraData_Export_Import.<b>def_NETWORK_MAP.ACTIVITY.1673849411</b>.log
hdfs dfs -get /user/def_network_maps/hdfs dfs -get 104.OneTicket_OraData_Import_Hive.<b>1673849411</b>.log
</pre>
3. Searches for Exception messages in log files  
`egrep '(Exception:|Coused by)' 10[1-4].OneTicket_OraData*.log`  
i.e.
<pre>
$ egrep '(Exception:|Coused by)' 10[1-4].OneTicket_OraData*.log
104.OneTicket_OraData_Import_Hive.1673849411.log:javax.security.sasl.SaslException: GSS initiate failed
104.OneTicket_OraData_Import_Hive.1673849411.log:Caused by: org.ietf.jgss.GSSException: No valid credentials provided (Mechanism level: Failed to find
</pre>
### Common errors  
  - impala/hive availability
  - Kerberos authentication
  *Ndef: The flow checks if the ticket is still active before any HDFS action.  
  In case of expiration the flow performs a `kinit` command*
## Data Check
Optional validation queries for verifying data completeness and load success.
The data checks below are provided for informational purposes only.  
If any of them returns wrong data, then no actions need to be taken from the support team.  
The flow runs periodically over the day and every time overwrites the data.   
### Check Load Status.
if the difference between `EXPORT_START_DT` and `IMPORT_START_DT` is greater than 2 hours it is considered as a problem in loading procedure.  
*Connect to Oracle (see [Database CLI commands](#database-cli-commands))*  
	<pre>
	select 
	  EXPORT_START_DT, IMPORT_START_DT,
	  case when 24*(EXPORT_START_DT-IMPORT_START_DT)>2 then 'ERROR' else 'OK' end Load_Status
	from EXPORT_CTL where EXPORT_SEQUENCE=0;
	</pre>
	<pre>
	EXPORT_START_DT     | IMPORT_START_DT     | LOAD_STATUS
	--------------------+---------------------+------------
	<b>2022-12-02 10:46:11 | 2022-12-02 07:48:26 | ERROR      </b>#in case of load issue
	
	EXPORT_START_DT     | IMPORT_START_DT     | LOAD_STATUS
	--------------------+---------------------+------------
	2022-12-02 10:46:11 | 2022-12-02 10:48:26 | OK         #under normal circumstances
	</pre>
### Check data in Hive-Impala tables
*Connect to Impala (see [Database CLI commands](#database-cli-commands))*  
```sql
select * from (
  select distinct  'activity' tbl, upd_ts from def_network_map.activity union all
  select distinct  'affected_customers', upd_ts from def_network_map.affected_customers union all
  select distinct  'affected_oct_wtt', upd_ts from def_network_map.affected_oct_wtt union all
  select distinct  'defective_netw_element', upd_ts from def_network_map.defective_netw_element union all
  select distinct  'open_mw', upd_ts from def_network_map.open_mw union all
  select distinct  'open_ntt', upd_ts from def_network_map.open_ntt union all
  select distinct  'open_oct', upd_ts from def_network_map.open_oct union all
  select distinct  'open_wtt', upd_ts from def_network_map.open_wtt
)a order by tbl
;

+------------------------+---------------------+
| tbl                    | upd_ts              |
+------------------------+---------------------+
| activity               | 2022-12-16 10:50:18 |
| affected_customers     | 2022-12-16 10:50:18 |
| affected_oct_wtt       | 2022-12-16 10:50:18 |
| defective_netw_element | 2022-12-16 10:50:18 |
| open_mw                | 2022-12-16 10:50:18 |
| open_ntt               | 2022-12-16 10:50:18 |
| open_oct               | 2022-12-16 10:50:18 |
| open_wtt               | 2022-12-16 10:50:18 |
+------------------------+---------------------+
Fetched 8 row(s) in 6.10s
```
`upd_ts` should have the same value *(+- 10 seconds)* as the one in `IMPORT_START_DT` from Oracle table `EXPORT_CTL`  
i.e.  
*Connect to Oracle (see [Database CLI commands](#database-cli-commands))*  
`select IMPORT_START_DT from EXPORT_CTL where EXPORT_SEQUENCE=0;`
```sql
IMPORT_START_DT     
--------------------
2022-12-16 10:50:19
```
*Conclusion: Hive/Impala tables contain the correct data according to the control table*
```
     upd_ts     = 2022-12-16 10:50:18 #Hive/Impala tables
IMPORT_START_DT = 2022-12-16 10:50:19 #Oracle Control Table
```