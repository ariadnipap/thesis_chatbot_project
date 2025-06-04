---
title: Reference Data ETL Flow
system: BigStreamer
component: Reference Data
job_name: refdata_etl
source_system: Local Filesystem (vantagerd)
source_tables:
  - cells_YYYYMMDD.csv.gz
  - crm_YYYYMMDD.csv.gz
  - devices_YYYYMMDD.csv.gz
  - services_YYYYMMDD.csv.gz
destination_system: Hive
destination_tables:
  - refdata.rd_cells_load
  - refdata.rd_services_load
  - refdata.rd_crm_load
  - refdata.rf_devices_load
schedule: daily at 00:05
coordinator: none (cron-based)
workflow: 210_refData_Load.sh / 220_refData_Daily_Snapshot.sh
script_path: /shared/abc/refdata/bin
monitoring_table: none
owner: intra
tags:
  - Reference Data
  - refdata
  - rd_cells_load
  - rd_crm_load
  - rd_services_load
  - rf_devices_load
  - Hive
  - Snapshot
  - Crontab
  - Bash Scripts
  - Troubleshooting
  - Data Validation
  - Vantagerd
---
# Reference Data Flow
This document describes the reference data ingestion process for cells, CRM, devices, and services. It includes file locations, loading scripts, cron scheduling, Hive targets, and troubleshooting steps.
## Installation info
Describes the input/output directories, involved nodes and users, script and log locations, and crontab setup for automatic file loading.
### Data Source File
- Local FileSystem Directories
  - host :`un2.bigdata.abc.gr (999.999.999.999)`
  - user : `vantagerd`
  - spool area : `/data/1/vantage_ref-data/REF-DATA/` link points to `/shared/vantage_ref-data/REF-DATA`
  - file_types : `<refType>_<refDate>.csv.gz`  
*\<refType\>: `cells, crm, devices, services` (i.e. cells_20230530.csv.gz)*
  - load_suffix : `<YYYYMMDD>.LOADED` *(i.e. cells_20230530.csv.cells_20230531.LOADED)*
- HDFS Directories
	- hdfs landingzone : `/ez/landingzone/REFDATA`
### Scripts-Logs Locations
- node : `un2.bigdata.abc.gr (999.999.999.999)`
- user : `intra`
- script path : `/shared/abc/refdata/bin`
- script files: 
	- `210_refData_Load.sh`
	- `220_refData_Daily_Snapshot.sh`
- log path : `/shared/abc/refdata/log`
- log files: 
	- `210_refData_Load.<YYYYMM>.log`
	- `220_refData_Daily_Snapshot.<YYYYMM>.log`
### Crontab Scheduling
- node : `un2.bigdata.abc.gr (999.999.999.999)`
- user : `intra`  
	runs at : Daily at 00:05
	`5 0 * * * /shared/abc/refdata/bin/210_refData_Load.sh CELLS $(date '+\%Y\%m\%d' -d "yesterday")`
Ndef1: The entry above loads reference data for CELLS.  
Ndef2: For each reference type a new entry of the `210_refData_Load.sh` is required passing the following parameters  
	\<reference Type\> : `cells, crm, devices, services`  
	\<reference Date\> : `yesterday` is the default value  
### Hive Tables
- Target Database: `refdata`
- Target Tables: 
	1. `rd_cells_load`
	1. `rd_services_load`
	1. `rd_crm_load`
	1. `rf_devices_load`
| Table Name         | Description                      |
|--------------------|----------------------------------|
| rd_cells_load      | Historical data of cell metadata |
| rd_services_load   | Historical data of services      |
| rd_crm_load        | Historical data of CRM records   |
| rf_devices_load    | Historical data of device info   |
## Data process
High-level overview of how reference files are prepared, parsed, and loaded into historical and snapshot Hive tables.
### High Level Overview
![High_Level_Overview](https://metis.ghi.com/obss/bigdata/abc/alarm-archiving/refdata/-/raw/main/docs/ReferenceData.High_Level_Overview.png)
##### Steps 1-3: 
abc is responsible for the preparation/creation of the Reference Data flat files.  
These files are stored into a specific directory in `UN2` node using the SFTP-PUT method as user `vantagerd`  
##### Steps 4-5:
Script `210_refData_Load.sh` is responsible to read, parse and load the contents of reference files into HIVE tables (aka LOAD tables).  
These tables keep the data of all completed loads. That is, they contain all the historicity of the reference data.  
The data of each load is stored in a separate partition identified by the date of the loading (i.e. par_dt=20230530)  
##### Steps 6-7:
Script `220_refData_Daily_Snapshot.sh` reads the most recently added data from the LOAD table and store them as a snapshot into a separate table (aka snapshot tables).  
The data of these tables are used for the enrichment of various fact data (i.e. Traffica (SAI))
## Manually Run
Instructions for manually triggering the data load process for a specific file and date using the load script.
`210_refData_Load.sh` script is responsible for the loading of a reference file.
To run the script two arguments are required  
`/shared/abc/refdata/bin/210_refData_Load.sh <refType>  <refDate>`  
1st: **\<refType\>**, the Reference Type
```
- CELLS
- CRM
- DEVICES
- SERVICES
```
2nd: **\<refDate\>**, the date that the flat file contains in its filename  
	i.e.
```
cells_20220207.csv.gz
cells_20220208.csv.gz
cells_20220209.csv.gz
services_20220207.csv.gz
devices_20220208.csv.gz
crm_20220209.csv.gz
```
In case of loading the files above we should execute the following commands
```bash
/shared/abc/refdata/bin/210_refData_Load.sh CELLS 20220207
/shared/abc/refdata/bin/210_refData_Load.sh cells 20220208
/shared/abc/refdata/bin/210_refData_Load.sh CELLS 20220209
/shared/abc/refdata/bin/210_refData_Load.sh services 20220207
/shared/abc/refdata/bin/210_refData_Load.sh DEVICES 20220208
/shared/abc/refdata/bin/210_refData_Load.sh crm 20220209
```
Once the loads completed, the flat files renamed to <CURRENT_YYYYMMDD>.LOADED
```
cells_20220207.csv.20230531.LOADED
cells_20220208.csv.20230531.LOADED
cells_20220209.csv.20230531.LOADED
services_20220207.csv.20230531.LOADED
devices_20220208.csv.20230531.LOADED
crm_20220209.csv.20230531.LOADED
```
## Troubleshooting
Explains how to identify and resolve issues with reference data loads using error logs and manual script execution.
**Currently, the Reference Data flow does not support the `Monitoring` services.**  
- An email will be sent by the system with the point of failure.
i.e.
```
Subject: ALERT: Reference data Loading, Type:CELL,  File:cells_20220207.csv
Body: 
	Reference Type  : CELL
	Reference File  : cells_20220207.csv
	Reference Scirpt: 210_refData_Load.sh
	------------------------------------------
	ERROR:$(date '+%F %T'), ALTER TABLE or LOAD DATA command failed.
```
- Check the log files for errors/exceptions  
```bash
egrep -i 'error|fail|exception|problem' /shared/abc/refdata/log/210_refData_Load.YYYYMM.log
egrep -i 'error|fail|exception|problem' /shared/abc/refdata/log/220_refData_Daily_Snapshot.YYYYMM.log
```
In case of failure follow the instructions described in **`Manually Run`**
### Common errors  
- Reference data file is empty or the contents of the file is not the expected.  
If this is the case, update abc that the file is invalid and ask them to send a new.  
- Other factors not related to the specific flow
	- impala/hive availability
	- Kerberos authentication
	*Ndef: The flow checks if the ticket is still active before any HDFS action.  
	In case of expiration the flow performs a `kinit` command*
## Data Check
Provides queries and instructions to verify data load completeness and partition existence in Hive tables.
- **Check final tables for new partitions**:
	```
	su - intra
	/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k -q "refresh refdata.rd_cells_load; show partitions refdata.rd_cells_load;"
	
	+----------+-----------+--------+---------+
	| par_dt   | #Rows     | #Files | Size    |
	+----------+-----------+--------+---------+
	| 20220227 | 98090     | 1      | 41.88MB |
	| 20220228 | 98021     | 1      | 41.84MB |
	| 20220301 | 97353     | 1      | 41.76MB |
	| Total    | 142404322 | 1500   | 59.63GB |
	+----------+-----------+--------+---------+
	```
- **Check the amount of data in final tables**:
```bash
su - intra
/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k -q "select par_dt, count(*) as cnt from refdata.rd_cells_load group by par_dt order by 1;"
	par_dt   | cnt    
	---------+--------
	20221130 | 2784494
```