---
title: IPVPN Application Flow  
description: Comprehensive architecture and pipeline for collecting, transforming, and exporting IP VPN network KPIs (CPU, memory, QoS, interface metrics) from NNM, SNMP, and UI-managed MySQL configurations into BigStreamer and the SQM system.  
system: BigStreamer  
component: IPVPN  
job_name: IPVPN_KPIs_Collection  
source_systems:  
  - HP Network Node Manager (NNM)  
  - SNMP Custom Poller  
  - Wildfly + MySQL (TrustCenter)  
destination_tables:  
  - bigcust.nnm_ipvpn_componentmetrics_hist  
  - bigcust.nnmcp_ipvpn_slametrics_hist  
  - bigcust.perf_interfacemetrics_ipvpn_hist  
  - bigcust.customer_pl  
  - bigcust.net_to_sm_customer  
  - bigcust.customer_sla_config_ipvpn  
  - bigcust.component_metrics  
  - bigcust.sla_metrics  
  - bigcust.interface_metrics  
schedule:  
  component_metrics_ingestion: every 5 minutes  
  sla_metrics_ingestion: every 5 minutes  
  interface_metrics_ingestion: every 2 minutes  
  postgres_config_sync: daily at 3:00 UTC  
  mysql_config_sync: daily at 4:00 UTC  
  kpi_exports_to_sqm: every 5 minutes  
  output_config_xml: every 4 hours  
source_transfer_protocols:  
  - SFTP  
  - Sqoop  
  - Spark  
  - Flume + Morphline  
  - SSH trigger  
key_users:  
  - ipvpn  
  - intra  
  - trustuser  
key_hosts:  
  - un2.bigdata.abc.gr  
  - nnmprd01.abc.gr  
  - nnmdis01.abc.gr  
  - unekl1.bigdata.abc.gr  
  - unekl2.bigdata.abc.gr  
  - unc1.bigdata.abc.gr  
  - unc2.bigdata.abc.gr  
sftp_paths:  
  - /var/opt/OV/shared/nnm/databases/custompoller/export/final  
  - /home/custompoller/ipvpn/out  
  - /home/custompoller/nnm_interface_metrics  
intermediate_paths:  
  - /data/1/nnm_components_LZ/spooldir  
  - /data/1/nnm_custompoller_ipvpn_LZ  
  - /shared/abc/ip_vpn/interfaces_flow/repo  
landingzone_paths:  
  - /ez/landingzone/nnm_custompoller_ipvpn/raw  
  - /shared/abc/ip_vpn/out/saismpm  
impala_tables:  
  - bigcust.nnm_ipvpn_componentmetrics_hist  
  - bigcust.nnmcp_ipvpn_slametrics_hist  
  - bigcust.perf_interfacemetrics_ipvpn_hist  
  - bigcust.customer_sla_config_ipvpn  
  - bigcust.customer_pl  
  - bigcust.net_to_sm_customer  
  - bigcust.pe_interfaces  
  - bigcust.sla_configurations  
  - bigcust.component_metrics  
  - bigcust.sla_metrics  
  - bigcust.interface_metrics  
mysql_tables:  
  - trustcenter.IPVPNCUUI_CUSTOMER_SLA_CONFIG  
  - trustcenter.IPVPNSLA_CUSTOMER_PL  
  - trustcenter.IPVPNSLA_NET_TO_SM_CUSTOMER  
  - trustcenter.IPVPNSLA_PE_INTERFACES  
postgre_tables:  
  - nnm.nms_iface  
  - nnm.nms_ip_addr  
  - nnm.nms_node  
scripts:  
  - load_data.pl  
  - spark-submit.sh  
  - update_pl_customer.sh  
  - update_net_to_sm_customer.sh  
  - update_customer_sla_config.sh  
  - update_pe_interfaces.sh  
  - initiate_export_components.sh  
  - initiate_export_sla.sh  
  - initiate_export_interfaces.sh  
  - populate_components_metrics_table.sh  
  - populate_sla_metrics_table.sh  
  - populate_interface_metrics_table.sh  
  - sftp.sh (XML Export)  
keywords:  
  - ipvpn  
  - vpn  
  - sla  
  - kpi  
  - snmp  
  - nnm  
  - wildfly  
  - trustcenter  
  - impala  
  - hdfs  
  - spark  
  - sqoop  
  - cron  
  - sftp  
  - flume  
  - morphline  
  - postgres  
  - mysql  
  - haproxy  
  - interface metrics  
  - qos  
  - memory  
  - cpu  
  - sqm  
  - perf metrics  
  - realtime kpis  
  - sla config  
  - oozie  
  - bigcust  
  - un2  
  - pipeline monitoring  
  - export retry  
---
# IPVPN
## Overview
Describes the architecture and flows that support the collection, processing, and storage of network KPIs for VPN customers.
IP VPN is an application that receives metrics about the network quality for the abc VPN Customers and produces Key Performance Indicators (KPIs) regarding Memory Usage, CPU Load, Provider Edge (PE) Interface, PE Branch Availability and PE Branch Quality of Service (QoS), which are collected and processed by the Service Management (SM) system of abc.
This is a document that will assist on support. Business documents can be found [here](https://metis.ghi.com/obss/bigdata/abc/ipvpn/ipvpnsla-customers-devops/-/tree/master/docs).
## Input Performance Data
Outlines how raw performance metrics are collected from NNM and SNMP systems, transferred to BigStreamer, and ingested into Impala.
There are two source systems, HP Network Node Manager (NNM) and SNMP Custom Poller application, that poll periodically network elements and produces raw files with the instantaneous metrics. These files are then parsed by one or more procedures. Finally they are loaded to BigStreamer cluster in Impala tables. There are 3 flows of input performance data that are being described in detail below.
### Component Metrics
Covers memory and CPU usage metrics collection from NNM and their ingestion via Flume.
#### Creation of raw files
The source system in this case is NNM. For high availability there are two instances of NNM on two separate servers and they operate in active-standby fashion. The whole infrastructure is entirely managed by abc. The raw files produced contain component metrics for CPU load and memory usage of the network elements and are stored in local paths on those servers.
``` mermaid
  graph TD
  A[Service: NNM <br> Host: nnmprd01.abc.gr] --> B[File: BIG-CUSTOMERS-CPU-MEM-UTIL_yyyymmddHHMMssSSS.csv.gz <br> Path: /var/opt/OV/shared/nnm/databases/custompoller/export/final <br> Host: nnmprd01.abc.gr]
  C[Service: NNM <br> Host: nnmdis01.abc.gr] -.->|Stopped| D[File: BIG-CUSTOMERS-CPU-MEM-UTIL_yyyymmddHHMMssSSS.csv.gz <br> Path: /var/opt/OV/shared/nnm/databases/custompoller/export/final <br> Host: nnmdis01.abc.gr]
```
- **Path**: `/var/opt/OV/shared/nnm/databases/custompoller/export/final` on `nnmprd01.abc.gr` or `nnmdis01.abc.gr`
- **File**: `BIG-CUSTOMERS-CPU-MEM-UTIL_yyyymmddHHMMssSSS.csv.gz`
- **Schedule**: `Every 5 minutes`
#### Transfer to BigStreamer nodes
A Perl script executed periodically by user `ipvpn` collects the raw files locally via passwordless SFTP, decompresses them and moves them to a local directory.
``` mermaid
  graph TD
  A[File: BIG-CUSTOMERS-CPU-MEM-UTIL_yyyymmddHHMMssSSS.csv.gz <br> Path: /var/opt/OV/shared/nnm/databases/custompoller/export/final <br> Host: nnmprd01.abc.gr] -->|SFTP| B[Path: /data/1/nnm_components_LZ <br> Host: un2.bigdata.abc.gr <br> User: ipvpn]
  B -->|Decompress/Move|C[Path: /data/1/nnm_components_LZ/spooldir <br> Host: un2.bigdata.abc.gr <br> User: ipvpn]
  D[File: BIG-CUSTOMERS-CPU-MEM-UTIL_yyyymmddHHMMssSSS.csv.gz <br> Path: /var/opt/OV/shared/nnm/databases/custompoller/export/final <br> Host: nnmdis01.abc.gr] -.->|Stopped| B
```
- **User**: `ipvpn`
- **Scheduler**: `Cron`
- **Schedule**: `Every minute`
- **SFTP Path**: `/var/opt/OV/shared/nnm/databases/custompoller/export/final`
- **SFTP user**: `custompoller`
- **Intermediate Path**: `/data/1/nnm_components_LZ`
- **Destination Path**: `/data/1/nnm_components_LZ/spooldir`
- **Logs**: /shared/abc/ip_vpn/log/nnm_component_metrics.cron.`date +%Y%m%d`.log
- **Configuration**: `/shared/abc/ip_vpn/DataParser/scripts/transferlist/cpu_mem.trn`
- **Script**: `/shared/abc/ip_vpn/DataParser/scripts/load_data.pl` on `un2.bigdata.abc.gr`
#### Load to BigStreamer cluster
Decompressed files are read on the spot by the Flume agent running on `un2.bigdata.abc.gr`. It first parses them using Morphline and then loads them into an Impala table.
``` mermaid
  graph TD
  A[File: BIG-CUSTOMERS-CPU-MEM-UTIL_yyyymmddHHMMssSSS.csv <br> Path: /data/1/nnm_components_LZ/spooldir <br> Host: un2.bigdata.abc.gr]
  B[Morphline Parsing]
  C[Impala Table: bigcust.nnm_ipvpn_componentmetrics_hist]
  A -->|Read| B
  B -->|Load| C
```
- **User**: `ipvpn`
- **Name**: `Flume-IPVPN` on `un2.bigdata.abc.gr`
- **Schedule**: `Always`
- **Source Path**: `/data/1/nnm_components_LZ/spooldir`
- **Morphline JAR**: `/home/users/ipvpn/flume-ipvpn/jars/nnmmetrics/lib/ipvpnsla-customers-abc-flume-2.0.0-SNAPSHOT.jar`
- **Morphline Configuration**: `/shared/abc/ip_vpn/flume/nnm_component_metrics/morphline_nnmMetricsCsvToRecord_ipvpn_user.conf`
- **Impala Table**: `bigcust.nnm_ipvpn_componentmetrics_hist`
- **Logs**: `/var/log/flume-ng/flume-cmf-flume5-AGENT-un2.bigdata.abc.gr.log*`
### SLA Metrics
Describes how SLA-related metrics are gathered, parsed, and loaded for QoS and availability KPIs.
#### Creation of raw files
The source system in this case is SNMP Custom Poller application. For high availability there are two deployments of the application on two seperate servers and they operate in active-standby fashion. While the servers are managed by abc, the application is managed by jkl. The raw files produced contain SLA metrics for QoS and availability of the network elements and are stored in local paths on those servers.
``` mermaid
  graph TD
  A[Service: SNMP Custom Poller <br> Host: nnmprd01.abc.gr] -.->|Stopped| B[File: nnmcp.*.yyyymmddHHMM.txt <br> Path: /home/custompoller/ipvpn/out <br> Host: nnmprd01.abc.gr]
  C[Service: SNMP Custom Poller <br> Host: nnmdis01.abc.gr] --> D[File: nnmcp.*.yyyymmddHHMM.txt <br> Path: /home/custompoller/ipvpn/out <br> Host: nnmdis01.abc.gr]
```
- **User**: `custompoller`
- **Scheduler**: `Cron`
- **Schedule**: `Every 5 minutes`
- **Path**: `/home/custompoller/ipvpn/out`
- **Elements Configuration**: `/home/custompoller/ipvpn/conf/vpn.config`
- **Logs**: /home/custompoller/ipvpn/log/ipvpn-`date +%Y%m%d`.log
- **Script**: `/home/custompoller/ipvpn/run/run_ipvpn.sh` on `nnmprd01.abc.gr` and `nnmdis01.abc.gr`
#### Transfer to BigStreamer nodes
A Perl script executed periodically by user `ipvpn` collects the raw files locally via passwordless SFTP, concatenates them into one for every 5 minute interval and uploads them to an HDFS directory.
``` mermaid
  graph TD
  A[File: nnmcp.*.yyyymmddHHMM.txt <br> Path: /home/custompoller/ipvpn/out <br> Host: nnmprd01.abc.gr]
  E[File: nnmcp.*.yyyymmddHHMM.txt <br> Path: /home/custompoller/ipvpn/out <br> Host: nnmdis01.abc.gr]
  B[Path: /data/1/nnm_custompoller_ipvpn_LZ <br> Host: un2.bigdata.abc.gr]
  C[File: nnm_poller_ipvpn.yyyymmddHHMM.yyyymmdd_HHMMss.group.parsed <br> Path: /data/1/nnm_custompoller_ipvpn_LZ <br> Host: un2.bigdata.abc.gr]
  D[Path: hdfs://nameservice1/ez/landingzone/nnm_custompoller_ipvpn/raw]
  A -.->|Stopped|B
  E --> |SFTP|B
  B -->|Concat|C
  C -->|Upload HDFS|D
```
- **User**: `ipvpn`
- **Scheduler**: `Executed from the previous step`
- **SFTP Path**: `/home/custompoller/ipvpn/out`
- **SFTP User**: `custompoller`
- **Intermediate Path**: `/data/1/nnm_custompoller_ipvpn_LZ`
- **Destination Path**: `hdfs://nameservice1/ez/landingzone/nnm_custompoller_ipvpn/raw`
- **Logs**: /shared/abc/nnm_custompoller_ipvpn/log/nnmcustompoller_ipvpn_cron.`date +%Y%m%d`.log
- **Configuration**: `/shared/abc/nnm_custompoller_ipvpn/DataParser/scripts_nnmprod/nnm_custompoller_ipvpn.trn`
- **Script**: `/shared/abc/nnm_custompoller_ipvpn/DataParser/scripts_nnmprod/nnm_custompoller_ipvpn.pl` on `un2.bigdata.abc.gr`
#### Load to BigStreamer cluster
A Spark job executed by the previous step parses the concatenated files and loads them into an Impala table.
> Ndef
>`spark-submit.sh` script is triggered in the following manner:
> 1.`run_ipvpn.sh` is run on nnmdis01 which triggers the execution of
> 2.`nnm_custompoller_ipvpn.pl` on un2 via ssh which runs
> 3. `spark_submit.sh` passed via `post_script` variable
``` mermaid
  graph TD
  A[File: nnm_poller_ipvpn.yyyymmddHHMM.yyyymmdd_HHMMss.group.parsed <br> Path: hdfs://nameservice1/ez/landingzone/nnm_custompoller_ipvpn/raw]
  B[Parsing]
  C[Impala Table: bigcust.nnmcp_ipvpn_slametrics_hist]
  A -->|Read| B
  B -->|Load| C
```
- **User**: `ipvpn`
- **Scheduler**: `Executed from the previous step`
- **Job Name**: `com.jkl.bigstreamer.ipvpnslacustomers.spark.snmp.SnmpETLTopologyRunner`
- **JAR**: `/home/users/ipvpn/run/ipvpnsla-customers-abc-spark.jar`
- **Logs**: /shared/abc/nnm_custompoller_ipvpn/log/nnmcustompoller_ipvpn_cron.`date +%Y%m%d`.log
- **Submit Script**: `/home/users/ipvpn/run/spark-submit.sh` on `un2.bigdata.abc.gr`
- **Impala Table**: `bigcust.nnmcp_ipvpn_slametrics_hist`
### Interface Metrics
Details metrics related to PE interface traffic and availability.
#### Creation of raw files
The source system in this case is NNM. For high availability there are two instances of NNM on two seperate servers and they operate in active-standby fashion. The whole infrastructure is entirely managed by abc. The raw files produced contain interface metrics for overall interfaces' usage of the network elements and are stored in local paths on those servers.
``` mermaid
  graph TD
  A[Service: NNM <br> Host: nnmprd01.abc.gr] --> B[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /files/_CUSTOM_POLLER_PROD/nnm_interface_metrics/vertica <br> Host: nnmprd01.abc.gr]
  C[Service: NNM <br> Host: nnmdis01.abc.gr] -.->|Stopped| D[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /files/_CUSTOM_POLLER_PROD/nnm_interface_metrics/vertica <br> Host: nnmdis01.abc.gr]
```
- **Source Path**: `/files/_CUSTOM_POLLER_PROD/nnm_interface_metrics/vertica` on `nnmprd01.abc.gr` or `nnmdis01.abc.gr`
- **File**: `InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz`
- **Schedule**: `Every 5 minutes`
Then a shell script running on the same servers, copies the files to the appropriate directory .
``` mermaid
  graph TD
  A[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /files/_CUSTOM_POLLER_PROD/nnm_interface_metrics/vertica <br> Host: nnmprd01.abc.gr]
  B[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /files/_CUSTOM_POLLER_PROD/nnm_interface_metrics/vertica <br> Host: nnmdis01.abc.gr]
  C[Script: transfer-new-files.sh <br> Host: nnmprd01.abc.gr <br> User: custompoller]
  D[Script: transfer-new-files.sh <br> Host: nnmdis01.abc.gr <br> User: custompoller]
  E[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /home/custompoller/nnm_interface_metrics <br> Host: nnmprd01.abc.gr]
  F[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /home/custompoller/nnm_interface_metrics <br> Host: nnmdis01.abc.gr]
  A --> C
  C --> E
  B -.->|Stopped| D
  D -.-> F
```
- **User**: `custompoller`
- **Scheduler**: `Cron`
- **Schedule**: `Every minute`
- **Path**: `/home/custompoller/nnm_interface_metrics`
- **Logs**: /home/custompoller/export_metrics/log/transfer-new-files.`date +%Y%m%d`.log
- **Script**: `/home/custompoller/export_metrics/transfer-new-files.sh` on `nnmprd01.abc.gr` or `nnmdis01.abc.gr`
#### Load to BigStreamer cluster
A Perl script executed periodically by user `ipvpn` collects the raw files locally via passwordless SFTP, decompresses them and uploads them to an Impala table.
``` mermaid
  graph TD
  A[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /home/custompoller/nnm_interface_metrics <br> Host: nnmprd01.abc.gr]
  B[File: InterfaceMetrics_yyyymmddHHMMssSSS.csv.gz <br> Path: /home/custompoller/nnm_interface_metrics <br> Host: nnmdis01.abc.gr]
  C[Path: /shared/abc/ip_vpn/interfaces_flow/repo <br> Host: un2.bigdata.abc.gr]
  D[Impala Table: bigcust.perf_interfacemetrics_ipvpn_hist]
  A -->|SFTP| C
  B -.->|Stopped|C
  C -->|Decompress/Load| D
```
- **User**: `ipvpn`
- **Scheduler**: `Cron`
- **Schedule**: `Every 2 minutes`
- **SFTP Path**: `/home/custompoller/nnm_interface_metrics`
- **SFTP user**: `custompoller`
- **Intermediate Path**: `/shared/abc/ip_vpn/interfaces_flow/repo`
- **Impala Table**: `bigcust.perf_interfacemetrics_ipvpn_hist`
- **Logs**: /shared/abc/ip_vpn/interfaces_flow/Dataparser/scripts/log/nnm_interface_metrics.cron.`date +%Y%m%d`.log
- **Configuration**: `/shared/abc/ip_vpn/interfaces_flow/Dataparser/scripts/transferlist/config_Interface_metrics.trn`
- **Script**: `/shared/abc/ip_vpn/interfaces_flow/Dataparser/scripts/load_data.pl` on `un2.bigdata.abc.gr`
## Input Configuration Data
Explains how network topology and configuration data from Postgres (NNM DB) are loaded to Impala for enrichment and join operations.
### NNM Postgres
The active NNM preserves network configuration data of the elements in a Postgres database, which is managed by abc. Every day these data are transferred to BigStreamer with Sqoop and used in computations of output performance data. Since slave nodes cannot connect directly to the Postgres database, firewall rules have been setup to `un1.bigdata.abc.gr` and `un2.bigdata.abc.gr` in order to forward requests to the external database.
``` bash
[root@un2 ~] firewall-cmd --list-all
public (active)
  target: ACCEPT
  icmp-block-inversion: no
  interfaces: bond0 bond0.100 bond0.2000 bond0.300 bond0.951 em2 lo p3p2
  sources:
  services: dhcpv6-client ssh
  ports:
  protocols:
  masquerade: yes
  forward-ports:
    ...
	port=6535:proto=tcp:toport=5432:toaddr=999.999.999.999
  source-ports:
  icmp-blocks:
  rich rules:
```
#### Table nms_iface
``` mermaid
  graph TD
  A[Postgres <br> Host: nnmprd01.abc.gr <br> Table: nnm.nms_iface ]
  B[Postgres <br> Host: nnmdis01.abc.gr <br> Table: nnm.nms_iface ]
  A -->|Sqoop| C[Impala Table: nnmnps.conf_nms_iface ]
  B -.->|Stopped| C
```
- **User**: `intra`
- **Scheduler**: `Oozie`
- **Schedule**: `Every day at 3:00 (UTC)`
- **Coordinator**: `Coord_nnmdb.nms_iface`
- **Troubleshooting Steps**:
- Identify service errors in the Coordinator's logs and tasks.
- Check if data have been loaded for a specific date using Impala shell or editor.
```bash
# e.g for 01-10-2018
select count(*) from nnmnps.conf_nms_iface where par_dt='20181001';
```
- Check if connectivity to Postgres works from `un2.bigdata.abc.gr`.
#### Table nms_ip_addr
``` mermaid
  graph TD
  A[Postgres <br> Host: nnmprd01.abc.gr <br> Table: nnm.nms_ip_addr ]
  B[Postgres <br> Host: nnmdis01.abc.gr <br> Table: nnm.nms_ip_addr ]
  A -->|Sqoop| C[Impala Table: nnmnps.nms_ip_addr ]
  B -.->|Stopped| C
```
- **User**: `intra`
- **Scheduler**: `Oozie`
- **Schedule**: `Every day at 3:00 (UTC)`
- **Coordinator**: `Coord_nnmdb.nms_ip_addr`
- **Troubleshooting Steps**:
- Identify service errors in the Coordinator's logs and tasks.
- Check if data have been loaded for a specific date using Impala shell or editor.
```bash
# e.g for 01-10-2018
select count(*) from nnmnps.nms_ip_addr where par_dt='20181001';
```
- Check if connectivity to Postgres works from `un2.bigdata.abc.gr`.
#### Table nms_node
``` mermaid
  graph TD
  A[Postgres <br> Host: nnmprd01.abc.gr <br> Table: nnm.nms_node ]
  B[Postgres <br> Host: nnmdis01.abc.gr <br> Table: nnm.nms_node ]
  A -->|Sqoop| C[Impala Table: nnmnps.nms_node ]
  B -.->|Stopped| C
```
- **User**: `intra`
- **Scheduler**: `Oozie`
- **Schedule**: `Every day at 3:00 (UTC)`
- **Coordinator**: `Coord_nnmdb.nms_node`
- **Troubleshooting Steps**:
- Identify service errors in the Coordinator's logs and tasks.
- Check if data have been loaded for a specific date using Impala shell or editor.
```bash
# e.g for 01-10-2018
select count(*) from nnmnps.nms_node where par_dt='20181001';
```
- Check that Coordinator runs correctly.  
```sql
SELECT MAX(par_dt) FROM nnmnps.nms_node WHERE par_dt>= from_timestamp(now() - interval 15 days,'yyyyMMdd')
```
must return the yesterday's date. 
- Check if connectivity to Postgres works from `un2.bigdata.abc.gr`.
### User Interface
Documents how user-managed configurations are handled by a web UI and synced to BigStreamer from MySQL.
#### Stack
Users can manage configurations used during the computation of the output performance data, using the CustomApps UI. The load balancer sends traffic to two Wildfly instances who keep track of users' changes in MySQL. They are updated into BigStreamer daily. The whole stack is managed by jkl.
``` mermaid
  graph TD
  A[Users] --> B[Load Balancer]
  B --> C[Wildfly <br> Host: unekl1.bigdata.abc.gr]
  B --> D[Wildfly <br> Host: unekl2.bigdata.abc.gr]
  C --> E[MySQL]
  D --> E
  E --> F[Sync MySQL and BigStreamer]
  F -->G[Impala]
```
##### Load Balancer
For load balancing the HaProxy service is used.
- **URL**: `https://cne.def.gr:8643/landing/#/login`
- **Controlled By**: `systemctl`
- **Configuration**: `/etc/haproxy/haproxy.cfg`
- **Host**: `unc1.bigdata.abc.gr` and `unc2.bigdata.abc.gr`
##### Wildfly
Wildfly is the application server used for the UI of CustomApps including IP VPN.
- **User**: `trustcenter`
- **Installation Path**: `/opt/trustcenter/wf_cdef_trc` on `unekl1.bigdata.abc.gr` and `unekl2.bigdata.abc.gr`
- **Deployments Path**: `/opt/trustcenter/wf_cdef_trc/standalone/deployments`
- **General Configuration Path**: `/opt/trustcenter/wf_cdef_trc/standalone/configuration/standalone-full.xml`
- **Application Configuration Path**: `/opt/trustcenter/wf_cdef_trc/standalone/configuration/ServiceWeaver/beanconfig/`
- **Application Logs**: `/opt/trustcenter/wf_cdef_trc/standalone/log/server.log`
- **Access Log**: `/opt/trustcenter/wf_cdef_trc/standalone/log/access_log.log`
##### MySQL
MySQL is the database used for the UI. Apart from other things, configuration data managed by users are stored there.
- **MySQL Servers**: `db01.bigdata.abc.gr` and `db02.bigdata.abc.gr` with vIP `999.999.999.999`
- **MySQL Schema**: `trustcenter`
#### Data Synchronization
Synchronization of MySQL and BigStreamer's data is done using Sqoop. These are data necessary for computation of the output performance metrics from MySQL used for UI to BigStreamer. Also steps to load configuration tables are done for improving query performance. The master scripts executes jobs in order to update the following Impala tables.
``` mermaid
  graph TD
  A[Oozie: Coord_IPVPN_load_mysql_to_Impala] -->|SSH| B[Host: un2.bigdata.abc.gr <br> User: intra2]
  B -->|sudo to ipvpn| C[Master Script]
```
- **User**: `intra`
- **Scheduler**: `Oozie`
- **Schedule**: `Every day at 4:00 (UTC)`
- **Coordinator**: `Coord_IPVPN_load_mysql_to_Impala`
- **Master Script**: `/shared/abc/ip_vpn/run/run_load_mysql_to_impala.sh`
- **Troubleshooting Steps**:
- Identify service errors in the Coordinator's logs and tasks.
##### Table customer_pl
Customer PL indicates which Packet Loss formula type is going to be used for each customer. Default is 1.
``` mermaid
graph TD
A[MySQL Table: trustcenter.IPVPNSLA_CUSTOMER_PL] -->|Sqoop| B[Impala Table: bigcust.customer_pl]
```
- **User**: `ipvpn`
- **Logs**: /shared/abc/ip_vpn/log/update_pl_customer.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/update_pl_customer.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log file.
##### Table net_to_sm_customer
Net to SM Customer is a translation for customer names from NNM to SM.
``` mermaid
graph TD
A[MySQL Table: trustcenter.IPVPNSLA_NET_TO_SM_CUSTOMER] -->|Sqoop| B[Impala Table: bigcust.net_to_sm_customer]
```
- **User**: `ipvpn`
- **Logs**: /shared/abc/ip_vpn/log/update_net_to_sm_customer.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/update_net_to_sm_customer.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log file.
##### Table customer_sla_config_ipvpn
SLA configurations specify how each QoS metric is computed.
``` mermaid
graph TD
A[MySQL Table: trustcenter.IPVPNCUUI_CUSTOMER_SLA_CONFIG] -->|Sqoop| B[Impala Table: bigcust.customer_sla_config_ipvpn]
```
- **User**: `ipvpn`
- **Logs**: /shared/abc/ip_vpn/log/update_customer_sla_config.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/update_customer_sla_config.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log file.
##### Table pe_interfaces
PE interfaces specify for which elements interface KPIs will be exported. The MySQL table is transferred to BigStreamer, enriched with NPS data and populates the Impala table. The enriched data are transferred back to MySQL.
``` mermaid
graph TD
A[MySQL Table: trustcenter.IPVPNSLA_PE_INTERFACES] -->|Sqoop| B[Impala Table: bigcust.pe_interfaces]
B -->|Sqoop| C[MySQL Table: trustcenter.IPVPNSLA_PE_INTERFACES_INTERMEDIATE]
C -->|MySQL Query|D[MySQL Table: trustcenter.IPVPNSLA_PE_INTERFACES]
```
- **User**: `ipvpn`
- **Logs**: /shared/abc/ip_vpn/log/update_pe_interfaces.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/update_pe_interfaces.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log file.
##### Table sla_configurations
Data from the above tables are combined and loaded into an Impala table used for queries of output performance metrics.
``` mermaid
graph TD
A[Impala Table: bigcust.customer_sla_config_ipvpn] --> B[Impala Table: bigcust.sla_configurations]
C[Impala Table: bigcust.customer_pl] --> B
D[Impala Table: bigcust.net_to_sm_customer] --> B
```
- **User**: `ipvpn`
- **Logs**: /shared/abc/ip_vpn/log/update_customer_sla_config.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/update_customer_sla_config.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log file.
## Output Performance Data
Describes how final KPIs (CPU, QoS, interface metrics) are calculated, stored, and sent to the SQM system.
For every 5-minute interval 5 HTTP requests containing CPU load, memory utilization, QoS, availability and interface utilization are sent to SQM server containing instantenous metrics for network elements and are moved to an exchange directory. Also these metrics are stored into an Impala table.
### CPU and Memory
#### Main script
A procedure is executed periodically that triggers IPVPN-SM App to compute and transmit to the SQM server via HTTP the metrics for CPU and memory KPIs of the network elements. The procedure also inserts the KPIs into an Impala table. These three sub-steps are executed in parallel.
- **User**: `ipvpn`
- **Scheduler**: `Cron`
- **Schedule**: `Every 5 minutes`
- **Exchange user**: `saismpm`
- **Exchange path**: `/shared/abc/ip_vpn/out/saismpm`
- **Logs**: /shared/abc/ip_vpn/log/initiate_export_components.cron.`date '+%Y%m%d'`.log
- **Script**: `/shared/abc/ip_vpn/run/initiate_export_components.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Check IPVPN-SM script and app [logs](/KnowledgeBase/abc/BigStreamer/supportDocuments/applicationFlows/ipvpn_sm_replacement.md#logs)
##### Load component_metrics
``` mermaid
graph TD
  A[Impala Table: bigcust.nnm_ipvpn_componentmetrics_hist]
  B[Computation of CPU & Memory KPIs]
  C[Impala Table: bigcust.component_metrics]
  A -->|Query|B
  B -->|Load|C
```
- **User**: `ipvpn`
- **Impala Table**: `bigcust.component_metrics`
- **Logs**: /shared/abc/ip_vpn/log/populate_components_metrics_table.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/populate_components_metrics_table.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log files e.g failed Impala query.
### QoS and Availability
#### Main script
A procedure is executed periodically that triggers IPVPN-SM App to compute and transmit to the SQM server via HTTP the metrics for QoS and availability KPIs of the network elements. The procedure also inserts the KPIs into an Impala table. These three sub-steps are executed in parallel.
- **User**: `ipvpn`
- **Scheduler**: `Cron`
- **Schedule**: `Every 5 minutes`
- **Exchange user**: `saismpm`
- **Exchange path**: `/shared/abc/ip_vpn/out/saismpm`
- **Logs**: /shared/abc/ip_vpn/log/initiate_export_sla.cron.`date '+%Y%m%d'`.log
- **Script**: `/shared/abc/ip_vpn/run/initiate_export_sla.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Check IPVPN-SM script and app [logs](/KnowledgeBase/abc/BigStreamer/supportDocuments/applicationFlows/ipvpn_sm_replacement.md#logs)
##### Load sla_metrics
``` mermaid
graph TD
  A[Impala Table: bigcust.nnmcp_ipvpn_slametrics_hist]
  B[Computation of QoS and AV KPIs]
  C[Impala Table: bigcust.sla_metrics]
  A -->|Query|B
  B -->|Load|C
```
- **User**: `ipvpn`
- **Impala Table**: `bigcust.sla_metrics`
- **Logs**: /shared/abc/ip_vpn/log/populate_sla_metrics_table.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/populate_sla_metrics_table.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log files e.g failed Impala query.
#### Support actions
Provides detailed instructions for identifying and resolving issues at any stage of the pipeline, from ingestion to SQM export.
##### Spark failure
If the ingestion of the SLA metrics failed during the spark job execution (meaning that the files are successfully moved to hdfs dir `/ez/landingzone/nnm_custompoller_ipvpn/raw` and they are ready to be loaded on the Impala table) then we can re-submit the spark job in the following manner:
1. Connect to un2 
``` bash
ssh un2
su - ipvpn
kinit -kt /home/users/ipvpn/ipvpn.keytab ipvpn
```
2. Execute the spark-submit as seen on file `/home/users/ipvpn/run/spark-submit.sh` with the appropriate startMin and endMin parameters
   e.g. for loading the metrics that correspond to the 5min interval `2023-11-29 11:20:00` :
```
spark-submit \
  --verbose  \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 4 \
  --files /home/users/ipvpn/ipvpn.keytab#ipvpn.keytab,/etc/hive/conf/hive-site.xml,/home/users/ipvpn/conf/ipvpn-log4j.xml#ipvpn-log4j.xml \
  --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=/home/users/ipvpn/conf/ipvpn-log4j.xml" \
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=/home/users/ipvpn/conf/ipvpn-log4j.xml" \
  --conf "spark.driver.extraJavaOptions=-DlogFilename=/home/users/ipvpn/log/ipvpn-" \
  --conf "spark.executor.extraJavaOptions=-DlogFilename=/home/users/ipvpn/log/ipvpn-" \
  --conf "spark.executor.instances=4" \
  --conf "spark.executor.cores=1" \
  --conf "spark.executor.memory=4g" \
  --conf "spark.executor.memoryOverhead=600" \
  --conf "spark.driver.cores=1" \
  --conf "spark.driver.memory=4g" \
  --conf "spark.driver.memoryOverhead=600" \
  --conf "spark.dynamicAllocation.enabled=false" \
  --class com.jkl.bigstreamer.ipvpnslacustomers.spark.snmp.SnmpETLTopologyRunner /home/users/ipvpn/run/ipvpnsla-customers-abc-spark.jar \
  -baseDirectory "hdfs://nameservice1/ez/landingzone/nnm_custompoller_ipvpn/raw/" -startMin 202311281120 -endMin 202311281120 -impalaTableName "bigcust.nnmcp_ipvpn_slametrics_hist" -counter32List "NumOfRTT,SumOfRTT,PacketLostSD,PacketLostDS,PacketMIA,NumJitOpCompletions,SumOfPosJitterSD,SumOfNegJitterSD,NumOfPosJitterSD,NumOfNegJitterSD,SumOfPosJitterDS,SumOfNegJitterDS,NumOfPosJitterDS,NumOfNegJitterDS,OperationCompletions,OperationTotInitiations" -totalDatasetPartitions 30
```
3. Check metrics are loaded
```
refresh nnmcp_ipvpn_slametrics_hist; 
select count(*) from nnmcp_ipvpn_slametrics_hist where n5_minute='2023-11-28 11:20:00';
```
### Interfaces
#### Main script
A procedure is executed periodically that triggers IPVPN-SM App to compute and transmit to the SQM server via HTTP the metrics for interface KPIs of the network elements. The procedure also inserts the KPIs into an Impala table. These two sub-steps are executed in parallel.
- **User**: `ipvpn`
- **Scheduler**: `Cron`
- **Schedule**: `Every 5 minutes`
- **Exchange user**: `saismpm`
- **Exchange path**: `/shared/abc/ip_vpn/out/saismpm`
- **Logs**: /shared/abc/ip_vpn/log/initiate_export_interfaces.cron.`date '+%Y%m%d'`.log
- **Master Script**: `/shared/abc/ip_vpn/run/initiate_export_interfaces.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Check IPVPN-SM script and app [logs](/KnowledgeBase/abc/BigStreamer/supportDocuments/applicationFlows/ipvpn_sm_replacement.md#logs)
##### Load interface_metrics
``` mermaid
graph TD
  A[Impala Table: bigcust.perf_interfacemetrics_ipvpn_hist]
  B[Computation of IF KPIs]
  C[Impala Table: bigcust.interface_metrics]
  A -->|Query|B
  B -->|Load|C
```
- **User**: `ipvpn`
- **Impala Table**: `bigcust.interface_metrics`
- **Logs**: /shared/abc/ip_vpn/log/populate_interface_metrics_table.`date +%Y%m%d`.log
- **Script**: `/shared/abc/ip_vpn/run/populate_interface_metrics_table.sh` on `un2.bigdata.abc.gr`
- **Troubleshooting Steps**:
- Identify system or service errors in the log files e.g failed Impala query.
## Output Configuration Data
Periodically an XML file that contains information about VPN customers with configuration changes, is produced by one of the Wildfly instances and is transferred to an exchange directory using a shell script.
``` mermaid
graph TD
  A[Wildfly <br> Host: unekl1.bigdata.abc.gr <br> Status: Master] -->| Executes | B[Script: /opt/trustcenter/wf_cdef_trc/ipvpnExports/sftp.sh <br> Host: unekl1.bigdata.abc.gr <br> User: trustuser]
  B -->|Export| C[File: SD_Inventory_DB_yyyy_mm_dd_HH:MM:SS.xml <br> Server: unekl1.bigdata.abc.gr]
  E[Wildfly <br> Host: unekl2.bigdata.abc.gr <br> Status: Slave] -.->| Executes | F[Script: /opt/trustcenter/wf_cdef_trc/ipvpnExports/sftp.sh <br> Host: unekl2.bigdata.abc.gr <br> User: trustuser]
  F -.->|Export| G[File: SD_Inventory_DB_yyyy_mm_dd_HH:MM:SS.xml <br> Server: unekl1.bigdata.abc.gr]
  C -->|SFTP| D[User: sd <br> Server: eeaadaptprd.def.gr <br> Path: /sd/classic/scripts/install/inventory/export/IPVPN_Inventory]
  G -.->|SFTP| D
```
- **User**: `trustuser`
- **Scheduler**: `Wildfly`
- **Schedule**: `Every 4 hours`
- **SFTP user**: `sd`
- **SFTP Server**: `eeaadaptprd.def.gr`
- **SFTP path**: `/sd/classic/scripts/install/inventory/export/IPVPN_Inventory`
- **Logs**: /opt/trustcenter/wf_cdef_trc/standalone/log/server.log*
- **Script**: `/opt/trustcenter/wf_cdef_trc/ipvpnExports/sftp.sh` on `unekl1.bigdata.abc.gr` and `unekl2.bigdata.abc.gr`