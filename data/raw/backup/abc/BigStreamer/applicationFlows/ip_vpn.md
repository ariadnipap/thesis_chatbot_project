# IPVPN Flow

## 1. Overview

IP VPN is an application that receives metrics about the network quality for the abc VPN Customers and produces Key Performance Indicators (KPIs) regarding Memory Usage, CPU Load, Provider Edge (PE) Interface, PE Branch Availability, and PE Branch Quality of Service (QoS), which are collected and processed by the Service Management (SM) system of abc.

This document assists in support. Business documents can be found [here](https://metis.ghi.com/obss/bigdata/abc/ipvpn/ipvpnsla-customers-devops/-/tree/master/docs).

## 2. Installation & Configuration

### Scripts & Configuration
- Install dependencies
- Configure Oozie

## 3. Data Processing

### 3.1. Input Performance Data

There are two source systems, HP Network Node Manager (NNM) and SNMP Custom Poller application, that poll network elements periodically and produce raw files with instantaneous metrics. These files are parsed by procedures and then loaded into the BigStreamer cluster in Impala tables.

There are 3 flows of input performance data described below.

#### 3.1.1. Component Metrics

##### 3.1.1.1. Creation of Raw Files

The source system for this flow is NNM. There are two instances of NNM operating in an active-standby mode. The raw files contain component metrics for CPU load and memory usage of network elements and are stored locally on these servers.

- **Path**: `/var/opt/OV/shared/nnm/databases/custompoller/export/final` on `nnmprd01.abc.gr` or `nnmdis01.abc.gr`
- **File**: `BIG-CUSTOMERS-CPU-MEM-UTIL_yyyymmddHHMMssSSS.csv.gz`
- **Schedule**: Every 5 minutes

##### 3.1.1.2. Transfer to BigStreamer Nodes

A Perl script executed by user `ipvpn` collects raw files via passwordless SFTP, decompresses them, and moves them to a local directory.

- **User**: `ipvpn`
- **Scheduler**: Cron
- **Schedule**: Every minute
- **SFTP Path**: `/var/opt/OV/shared/nnm/databases/custompoller/export/final`
- **SFTP User**: `custompoller`
- **Intermediate Path**: `/data/1/nnm_components_LZ`
- **Destination Path**: `/data/1/nnm_components_LZ/spooldir`
- **Logs**: `/shared/abc/ip_vpn/log/nnm_component_metrics.cron.<date>.log`
- **Configuration**: `/shared/abc/ip_vpn/DataParser/scripts/transferlist/cpu_mem.trn`
- **Script**: `/shared/abc/ip_vpn/DataParser/scripts/load_data.pl` on `un2.bigdata.abc.gr`

##### 3.1.1.3. Load to BigStreamer Cluster

Decompressed files are read by a Flume agent running on `un2.bigdata.abc.gr`. It parses them using Morphline and loads them into an Impala table.

- **User**: `ipvpn`
- **Name**: `Flume-IPVPN` on `un2.bigdata.abc.gr`
- **Schedule**: Always
- **Source Path**: `/data/1/nnm_components_LZ/spooldir`
- **Morphline JAR**: `/home/users/ipvpn/flume-ipvpn/jars/nnmmetrics/lib/ipvpnsla-customers-abc-flume-2.0.0-SNAPSHOT.jar`
- **Morphline Configuration**: `/shared/abc/ip_vpn/flume/nnm_component_metrics/morphline_nnmMetricsCsvToRecord_ipvpn_user.conf`
- **Impala Table**: `bigcust.nnm_ipvpn_componentmetrics_hist`
- **Logs**: `/var/log/flume-ng/flume-cmf-flume5-AGENT-un2.bigdata.abc.gr.log*`

#### 3.1.2. SLA Metrics

##### 3.1.2.1. Creation of Raw Files

The source system here is the SNMP Custom Poller application. It produces SLA metrics for QoS and availability of network elements.

- **User**: `custompoller`
- **Scheduler**: Cron
- **Schedule**: Every 5 minutes
- **Path**: `/home/custompoller/ipvpn/out`
- **Elements Configuration**: `/home/custompoller/ipvpn/conf/vpn.config`
- **Logs**: `/home/custompoller/ipvpn/log/ipvpn-<date>.log`
- **Script**: `/home/custompoller/ipvpn/run/run_ipvpn.sh` on `nnmprd01.abc.gr` and `nnmdis01.abc.gr`

##### 3.1.2.2. Transfer to BigStreamer Nodes

A Perl script executed by `ipvpn` collects raw files, concatenates them into one for every 5-minute interval, and uploads them to an HDFS directory.

- **User**: `ipvpn`
- **Scheduler**: Executed from the previous step
- **SFTP Path**: `/home/custompoller/ipvpn/out`
- **SFTP User**: `custompoller`
- **Intermediate Path**: `/data/1/nnm_custompoller_ipvpn_LZ`
- **Destination Path**: `hdfs://nameservice1/ez/landingzone/nnm_custompoller_ipvpn/raw`
- **Logs**: `/shared/abc/nnm_custompoller_ipvpn/log/nnmcustompoller_ipvpn_cron.<date>.log`
- **Configuration**: `/shared/abc/nnm_custompoller_ipvpn/DataParser/scripts_nnmprod/nnm_custompoller_ipvpn.trn`
- **Script**: `/shared/abc/nnm_custompoller_ipvpn/DataParser/scripts_nnmprod/nnm_custompoller_ipvpn.pl` on `un2.bigdata.abc.gr`

##### 3.1.2.3. Load to BigStreamer Cluster

A Spark job parses concatenated files and loads them into an Impala table.

- **User**: `ipvpn`
- **Scheduler**: Executed from the previous step
- **Job Name**: `com.jkl.bigstreamer.ipvpnslacustomers.spark.snmp.SnmpETLTopologyRunner`
- **JAR**: `/home/users/ipvpn/run/ipvpnsla-customers-abc-spark.jar`
- **Logs**: `/shared/abc/nnm_custompoller_ipvpn/log/nnmcustompoller_ipvpn_cron.<date>.log`
- **Submit Script**: `/home/users/ipvpn/run/spark-submit.sh` on `un2.bigdata.abc.gr`
- **Impala Table**: `bigcust.nnmcp_ipvpn_slametrics_hist`

## 4. Monitoring & Debugging

### Logs
- Logs stored in `/var/logs`
- Application logs can be found in each Workflow in Hue as user `ipvpn`. 
- Oozie Coordinator results can be seen in HUE (login as `ipvpn` user) under `Jobs -> Workflows`

#### Monitoring Metrics

- All monitoring messages have the following constant values:  
  **Application:** `IPVPN`  
  **Job:** `METRICS_PROCESSING`
- All monitoring messages of the same execution have a **unique executionId**
- Every component of one execution has a unique row that is updated between the following status values: `RUNNING → SUCCESS` or `FAILED`.

##### Checking Monitoring App for Successful Executions

curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=IPVPN&job=METRICS_PROCESSING&status=SUCCESS&operativePartition=<timestamp e.g.:20220518>'

##### Checking Monitoring App for Failed Executions

curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=IPVPN&job=METRICS_PROCESSING&status=FAILED&operativePartition=<timestamp e.g.:20220518>'

#### Grafana Dashboard

    Grafana Link: https://unc1.bigdata.abc.gr:3000/d/IPVPN/ipvpn-dashboard?orgId=1&from=now-2d&to=now

## 5. Troubleshooting
### 5.1. Oracle Connection Issues

If data are not being ingested, verify Oracle connectivity:

ssh <username>@un2
sh -l intra
jsec_file=jceks://hdfs/ez/intra.Sqoop.Creds.jceks
sqoop eval \
-Dhadoop.security.credential.provider.path=${jsec_file} \
--password-alias dm_sas_va.pass \
--connect jdbc:oracle:thin:@999.999.999.999:6644/DWHPRD \
--username dm_sas_va \
--query "SELECT * FROM SAS_VA_VIEW.V_DW_CONTROL_TABLE WHERE 1=1";

### 5.2. Hive/Impala Query Failures

    Log in to HUE UI
    Click on Editor -> Hive/Impala
    Run the following query:

SELECT * FROM bigcust.nnm_ipvpn_componentmetrics_hist LIMIT 3;

### 5.3. Spark Job Failures

If the ingestion of SLA metrics failed during the Spark job execution (i.e., files are successfully moved to HDFS but not loaded into Impala), resubmit the job:

    Connect to un2

ssh un2
su - ipvpn
kinit -kt /home/users/ipvpn/ipvpn.keytab ipvpn

    Execute the spark-submit script manually:

spark-submit \
  --verbose  \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 4 \
  --files /home/users/ipvpn/ipvpn.keytab#ipvpn.keytab,/etc/hive/conf/hive-site.xml,/home/users/ipvpn/conf/ipvpn-log4j.xml#ipvpn-log4j.xml \
  --class com.jkl.bigstreamer.ipvpnslacustomers.spark.snmp.SnmpETLTopologyRunner \
  /home/users/ipvpn/run/ipvpnsla-customers-abc-spark.jar \
  -baseDirectory "hdfs://nameservice1/ez/landingzone/nnm_custompoller_ipvpn/raw/" \
  -startMin 202311281120 -endMin 202311281120 \
  -impalaTableName "bigcust.nnmcp_ipvpn_slametrics_hist"

    Verify the data load:

REFRESH nnmcp_ipvpn_slametrics_hist;
SELECT COUNT(*) FROM nnmcp_ipvpn_slametrics_hist WHERE n5_minute='2023-11-28 11:20:00';

## 6. Data Validation & Checks

    Step 1: Verify raw files exist in source directories:

ls -l /home/custompoller/ipvpn/out/

    Step 2: Check HDFS ingestion:

hdfs dfs -ls /ez/landingzone/nnm_custompoller_ipvpn/raw/

    Step 3: Verify Impala data consistency:

SELECT COUNT(*) FROM bigcust.nnmcp_ipvpn_slametrics_hist WHERE par_dt='20231001';

## 7. Miscellaneous Notes

    SFTP Credentials: custompoller user with passwordless authentication
    BigStreamer Cluster: un2.bigdata.abc.gr
    Monitoring Alerts: Emails sent upon failure to pre-configured support team
    Performance Metrics: 5-minute granularity for CPU, Memory, QoS, Availability, and Interfaces
