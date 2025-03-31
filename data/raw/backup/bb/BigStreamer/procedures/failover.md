# Failover Procedure

## Description

This procedure outlines the steps required to failover applications and procedures from the active production (PR) site to the disaster recovery (DR) site in case of major failures.
Prerequisites

    Two symmetrical clusters (PR and DR).
    Streaming and batch procedures running in both sites.
    External traffic and UC4 flows only active in one site at a time.

## Procedure Steps
### 1. Stop Streaming Procedures
#### 1.1 Stop Production IBank, Online Spark Topologies

    Login with your personal account at dr1edge01 or pr1edge01, based on the site that will be stopped.
    Switch user to PRODREST.
    Comment out lines in crontab that run:

/opt/ingestion/PRODREST/common/scripts/restart_topology_STABLE.sh
/opt/ingestion/PRODREST/common/scripts/restart_visible_topology.sh

Create SHUTDOWN markers:

[PRODREST@Xr1edge01]# touch SHUTDOWN
[PRODREST@Xr1edge01]# hdfs dfs –put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest/topology_shutdown_marker/
[PRODREST@Xr1edge01]# hdfs dfs –put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest_Visible/topology_shutdown_marker/
[PRODREST@Xr1edge01]# hdfs dfs –put SHUTDOWN /user/PRODREST/service/PROD_Online_Ingest/topology_shutdown_marker/

Wait for 5 minutes and verify that applications are no longer running:

    [PRODREST@Xr1edge01]# yarn application –list | grep PRODUSER

#### 1.2 Stop Development IBank, Online Spark Topologies (Only on DR)

    Login with your personal account at dr1edge01.
    Switch user to DEVREST.
    Comment out lines in crontab that run:

/opt/ingestion/DEVREST/common/scripts/restart_topology.sh

Create SHUTDOWN markers:

[DEVREST@dr1edge01]# touch SHUTDOWN
[DEVREST@dr1edge01]# hdfs dfs –put SHUTDOWN /user/DEVREST/service/DEV_IBank_Ingest/topology_shutdown_marker/
[DEVREST@dr1edge01]# hdfs dfs –put SHUTDOWN /user/DEVREST/service/DEV_Online_Ingest/topology_shutdown_marker/

Wait for 5 minutes and verify that applications are no longer running:

    [DEVREST@dr1edge01]# yarn application –list | grep DEVREST

### 2. Stop Batch Procedures
#### 2.1 Disable Daily and Hourly IBank Production Batch Jobs

    Login with your personal account at dr1edge01 or pr1edge01.
    Switch user to PRODREST.
    Comment out lines in crontab that run:

/opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh
/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh

Check that batch jobs are not already running:

    [PRODREST@Xr1edge01]# ps -ef | grep 'ibank_histMigrate_aggr_MergeBatchWithLock'
    [PRODREST@Xr1edge01]# ps -ef | grep 'submitmnoSparkTopology_batch_cluster_mno_hourly'

    If jobs are running, wait for them to stop.

#### 2.2 Disable Daily and Hourly Online Production Batch Jobs

    Login with your personal account at dr1edge01 or pr1edge01.
    Switch user to PRODREST.
    Comment out lines in crontab that run:

/opt/ingestion/PRODREST/common/scripts/online_daily_batch_jobs_STABLE.sh
/opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh

Check that batch jobs are not already running:

    [PRODREST@Xr1edge01]# ps -ef | grep 'online_daily_batch_jobs_STABLE'
    [PRODREST@Xr1edge01]# ps -ef | grep 'submitmnoSparkTopology_batch_cluster_mno_hourly'

    If jobs are running, wait for them to stop.

#### 2.3 Disable Daily IBank, Online Development Batch Jobs (Only on DR)

    Login with your personal account at dr1edge01.
    Switch user to DEVREST.
    Comment out lines in crontab that run:

/opt/ingestion/DEVREST/common/scripts/cronExecutor_MergeBatchWithLock_hdfs.sh

Check that batch jobs are not already running:

    [DEVREST@Xr1edge01]# ps -ef | grep 'cronExecutor_MergeBatchWithLock_hdfs'

    If jobs are running, wait for them to stop.

### 3. Migrate Traffic Between DR/PR

    Start prodrestib and prodreston Wildfly instances on the other site.
    Contact mno Network administrators to request a network switch.
    Verify that new Wildfly instances are working via logs.
    Once verified, ask to disable the old servers.
    Confirm that no traffic is received on old servers via access logs.
    Stop the old Wildfly instances.

### 4. Migrate UC4 Flows Between PR/DR

    Login to edge servers of both sites and switch to root.
    Stop UC4 agent on the active site:

systemctl stop uc4agent

Start UC4 agent on the passive site:

systemctl start uc4agent

Add last successful execution of IBank DataWarehouse on passive site:

sudo -u PRODUSER /opt/ingestion/PRODUSER/datawarehouse-ibank/insert_rows_dwh_monitoring.sh <date>

Update trigger file creation:

    On active site, comment out:

vi /opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh
# touch /home/bank_central_mno_gr/datawarehouse_status/IBANK_SA_`date '+%Y%m%d'`.READY
# touch /opt/applications/landing_zone/PRODUSER/triggers/IBANK_SA_`date '+%Y%m%d'`.READY

On passive site, uncomment:

        vi /opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh
        # touch /home/bank_central_mno_gr/datawarehouse_status/IBANK_SA_`date '+%Y%m%d'`.READY
        # touch /opt/applications/landing_zone/PRODUSER/triggers/IBANK_SA_`date '+%Y%m%d'`.READY

## Actions Taken / Expected Output

    All batch and streaming procedures should be disabled on the failing site.
    UC4 agent should be migrated successfully.
    Wildfly instances should be properly switched to the standby site.
    External traffic should be routed to the active site.

## Notes and Warnings

    Ensure that all procedures have stopped before starting them on the standby site. Verify network traffic and application logs to confirm a successful failover.

## Affected Systems / Scope

    PR and DR clusters.
    Streaming and batch ingestion processes.
    External traffic and UC4 workflows.

## Troubleshooting / Error Handling

    If batch jobs fail to stop, manually kill the processes.
    If network migration fails, revert to the previous setup and investigate logs.

## References


