---
title: BigStreamer PR-DR Failover Procedure
description: Step-by-step failover procedure for BigStreamer cluster environments from production (PR) to disaster recovery (DR) site, including stopping streaming/batch jobs, migrating UC4 agents, switching Wildfly traffic, and updating external flows.
tags:
  - failover
  - dr
  - disaster-recovery
  - uc4
  - spark
  - streaming
  - batch
  - wildfly
  - bigstreamer
  - hdfs
  - yarn
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  clusters:
    - production
    - disaster recovery
  services:
    - Spark Streaming
    - Wildfly
    - UC4
    - HDFS
    - Yarn
  users:
    - PRODREST
    - DEVREST
    - PRODUSER
  systems:
    - dr1edge01
    - pr1edge01
    - edge nodes
    - cluster load balancer
---
# Failover
## Scope
In case that the active site faces multiple issues that cannot be resolved in a small amount of time, we need to failover applications and procedures to the standby one. 
## Setup
Two symmetrical clusters have been setup named production (PR) and disaster (DR). Streaming and batch procedures are running in both sites. External traffic and UC4 flows however are only active in one of them. 
## Procedure
### Stop Spark Streaming Topologies (PROD & DEV)
This section describes how to gracefully shut down Spark Streaming topologies on the currently active site (PROD or DR), by disabling crontab restarts and creating shutdown markers in HDFS.
1. Stop production IBank, Online Spark topologies:
- Login with your personal account at `dr1edge01` or `pr1edge01`, based on the site that will be stopped.
- Switch user to `PRODREST`.
- Comment lines in crontab that run `/opt/ingestion/PRODREST/common/scripts/restart_topology_STABLE.sh` and `/opt/ingestion/PRODREST/common/scripts/restart_visible_topology.sh`.
- Create `SHUTDOWN` markers for the Spark topologies.
```bash
[PRODREST@Xr1edge01]# touch SHUTDOWN
[PRODREST@Xr1edge01]# hdfs dfs -put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest/topology_shutdown_marker/
[PRODREST@Xr1edge01]# hdfs dfs -put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest_Visible/topology_shutdown_marker/
[PRODREST@Xr1edge01]# hdfs dfs -put SHUTDOWN /user/PRODREST/service/PROD_Online_Ingest/topology_shutdown_marker/
```
- Wait for 5 minutes and check that the above applications are no longer running.
```bash
[PRODREST@Xr1edge01]# yarn application -list | grep PRODUSER
```
1. Stop development IBank, Online Spark topologies:
- Login with your personal account at `dr1edge01`. **This is done only on DR site**
- Switch user to `DEVREST`.
- Comment line in crontab that run `/opt/ingestion/DEVREST/common/scripts/restart_topology.sh`.
- Create `SHUTDOWN` markers for the Spark topologies. 
```bash
[DEVREST@dr1edge01]# touch SHUTDOWN
[DEVREST@dr1edge01]# hdfs dfs -DEV_IBank_Ingest/topology_shutdown_marker/
[DEVREST@dr1edge01]# hdfs dfs -put SHUTDOWN /user/DEVREST/service/DEV_Online_Ingest/topology_shutdown_marker/
```
- Wait for 5 minutes and check that the above applications are no longer running.
``` bash
[DEVREST@dr1edge01]# yarn application -list | grep DEVREST
```
### Stop Batch Jobs (PROD & DEV)
This section explains how to disable hourly and daily batch jobs for IBank and Online applications in both production and development environments, by commenting crontab lines and checking for active processes.
1. Disable daily and hourly IBank production batch jobs
- Login with your personal account at `dr1edge01` or `pr1edge01`, based on the site that will be stopped.
- Switch user to `PRODREST`.
- Comment lines in crontab that run `/opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh` and `/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh`.
- Check that batch jobs are not already running.
```bash
[PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh'
[PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh'
```
- If they are already running wait for them to stop.
2. Disable daily and hourly Online production batch jobs:
- Login with your personal account at `dr1edge01` or `pr1edge01`, based on the site that will be stopped.
- Switch user to `PRODREST`.
- Comment lines in crontab that run `/opt/ingestion/PRODREST/common/scripts/online_daily_batch_jobs_STABLE.sh` and `/opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh`.
- Check that batch job is not already running.
```bash
[PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/common/scripts/online_daily_batch_jobs_STABLE.sh'
[PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh'
```
- If they are already running wait for them to stop.
3. Disable daily IBank, Online development batch jobs:
- Login with your personal account at `dr1edge01`. **This is done only on DR site**
- Switch user to `DEVREST`.
- Comment lines that run `/opt/ingestion/DEVREST/common/scripts/cronExecutor_MergeBatchWithLock_hdfs.sh` in crontab.
- Check that batch jobs are not already running.
```bash
[DEVREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/DEVREST/common/scripts/cronExecutor_MergeBatchWithLock_hdfs.sh'
```
- If they are already running wait for them to stop.
### Migrate Wildfly Traffic to DR Site
This section covers how to shift Wildfly application traffic (IBank and Online) from the active to the standby site, by launching Wildfly on the DR edge nodes and coordinating with network administrators for load balancer changes.
1. Start `prodrestib` Wildfly instances at both edge nodes of the other site using this [procedure](manage_wildfly.md#start-a-wildfly-instance-prodrestib).
2. Start `prodreston` Wildfly instances at both edge nodes of the other site using this [procedure](manage_wildfly.md#start-a-wildfly-instance-prodreston).
3. Ask for a mno Network administrator to make a call.
4. Ask them to enable the new servers (mention the Loadbalancer IPs and the IP you want them to enable as explained [here](manage_wildfly.md#consolidated-network-information)).
5. Check logs for both Wildfly instances at both servers to ensure everything works.
6. When you are certain everything is OK, ask the mno Network administrators to disable the prexisting servers (mention the Loadbalancer IPs and the IP you want them to disable).
7. From the access logs of the prexisting Wildfly instances check that no traffic is received. 
8. Stop these Wildfly instances as described in the procedures [here](manage_wildfly.md#stop-a-wildfly-instance-prodrestib) and [here](manage_wildfly.md#stop-a-wildfly-instance-prodreston).
### Migrate UC4 Agent and External Trigger Handling
This section outlines the process of moving the UC4 job scheduler and external trigger file creation logic from the primary site to the DR site, including enabling UC4 agents, updating job scripts, and ensuring data warehouse monitoring continues without interruption.
1. Login to the edge servers of the active and passive site using your personal account and become `root`.
2. Stop UC4 agent at the edge nodes of the active site.
```bash
systemctl stop uc4agent
```
3. Start service for UC4 agent at the edge servers of the passive site.
```bash
systemctl start uc4agent
```
4. Add entries for last successful execution of IBank DataWarehouse at the edge servers of the passive site.
```bash
sudo -u PRODUSER /opt/ingestion/PRODUSER/datawarehouse-ibank/insert_rows_dwh_monitoring.sh <date> 
# Use the previous day's date in YYYYMMdd format.
# If today is Sunday or Monday, use the date of the last Friday instead.
```
5. Migrate the creation of trigger files for external jobs
- On the active site:
```bash
vi /opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh
# Comment the followin lines along with the assosiated checks
# touch /home/bank_central_mno_gr/datawarehouse_status/IBANK_SA_`date '+%Y%m%d'`.READY
# touch /opt/applications/landing_zone/PRODUSER/triggers/IBANK_SA_`date '+%Y%m%d'`.READY
```  
- On the passive site:
```bash
vi /opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh
# Uncomment the followin lines along with the assosiated checks
# touch /home/bank_central_mno_gr/datawarehouse_status/IBANK_SA_`date '+%Y%m%d'`.READY
# touch /opt/applications/landing_zone/PRODUSER/triggers/IBANK_SA_`date '+%Y%m%d'`.READY
```
### Revert Failover to PR
>To revert the failover and restore traffic back to PR, repeat the above steps in reverse order, starting by stopping all workloads and UC4 agents in DR and reactivating them in PR.