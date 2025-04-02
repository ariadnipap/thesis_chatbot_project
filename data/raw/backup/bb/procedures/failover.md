# Failover

- [Failover](#failover)
  - [Scope](#scope)
  - [Setup](#setup)
  - [Procedure](#procedure)
    - [Stop streaming procedures](#stop-streaming-procedures)
    - [Stop batch procedures](#stop-batch-procedures)
    - [Migrate traffic between DR/PR](#migrate-traffic-between-drpr)
    - [Migrate UC4 flows between PR/DR](#migrate-uc4-flows-between-prdr)

## Scope

In case that the active site faces multiple issues that cannot be resolved in a small amount of time, we need to failover applications and procedures to the standby one. 

## Setup

Two symmetrical clusters have been setup named production (PR) and disaster (DR). Streaming and batch procedures are running in both sites. External traffic and UC4 flows however are only active in one of them. 

## Procedure

### Stop streaming procedures

1. Stop production IBank, Online Spark topologies:

    - Login with your personal account at `dr1edge01` or `pr1edge01`, based on the site that will be stopped.
    - Switch user to `PRODREST`.
    - Comment lines in crontab that run `/opt/ingestion/PRODREST/common/scripts/restart_topology_STABLE.sh` and `/opt/ingestion/PRODREST/common/scripts/restart_visible_topology.sh`.
    - Create `SHUTDOWN` markers for the Spark topologies.
      
      ``` bash
      [PRODREST@Xr1edge01]# touch SHUTDOWN
      [PRODREST@Xr1edge01]# hdfs dfs –put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest/topology_shutdown_marker/
      [PRODREST@Xr1edge01]# hdfs dfs –put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest_Visible/topology_shutdown_marker/
      [PRODREST@Xr1edge01]# hdfs dfs –put SHUTDOWN /user/PRODREST/service/PROD_Online_Ingest/topology_shutdown_marker/
      ```
    - Wait for 5 minutes and check that the above applications are no longer running.

      ``` bash
      [PRODREST@Xr1edge01]# yarn application –list | grep PRODUSER
      ```

1. Stop development IBank, Online Spark topologies:

    - Login with your personal account at `dr1edge01`. **This is done only on DR site**
    - Switch user to `DEVREST`.
    - Comment line in crontab that run `/opt/ingestion/DEVREST/common/scripts/restart_topology.sh`.
    - Create `SHUTDOWN` markers for the Spark topologies.
      
      ``` bash
      [DEVREST@dr1edge01]# touch SHUTDOWN
      [DEVREST@dr1edge01]# hdfs dfs –put SHUTDOWN /user/DEVREST/service/DEV_IBank_Ingest/topology_shutdown_marker/
      [DEVREST@dr1edge01]# hdfs dfs –put SHUTDOWN /user/DEVREST/service/DEV_Online_Ingest/topology_shutdown_marker/
      ```
    - Wait for 5 minutes and check that the above applications are no longer running.

      ``` bash
      [DEVREST@dr1edge01]# yarn application –list | grep DEVREST
      ```

### Stop batch procedures

1. Disable daily and hourly IBank production batch jobs:

    - Login with your personal account at `dr1edge01` or `pr1edge01`, based on the site that will be stopped.
    - Switch user to `PRODREST`.
    - Comment lines in crontab that run `/opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh` and `/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh`.
    - Check that batch jobs are not already running.

      ``` bash
      [PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh'
      [PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh'
      ```
    - If they are already running wait for them to stop.
  
2. Disable daily and hourly Online production batch jobs:

    - Login with your personal account at `dr1edge01` or `pr1edge01`, based on the site that will be stopped.
    - Switch user to `PRODREST`.
    - Comment lines in crontab that run `/opt/ingestion/PRODREST/common/scripts/online_daily_batch_jobs_STABLE.sh` and `/opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh`.
    - Check that batch job is not already running.

      ``` bash
      [PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/common/scripts/online_daily_batch_jobs_STABLE.sh'
      [PRODREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_batch_cluster_mno_hourly_STABLE.sh'
      ```
    - If they are already running wait for them to stop.

3. Disable daily IBank, Online development batch jobs:

    - Login with your personal account at `dr1edge01`. **This is done only on DR site**
    - Switch user to `DEVREST`.
    - Comment lines that run `/opt/ingestion/DEVREST/common/scripts/cronExecutor_MergeBatchWithLock_hdfs.sh` in crontab.
    - Check that batch jobs are not already running.

      ``` bash
      [DEVREST@Xr1edge01]# ps -ef | grep '/opt/ingestion/DEVREST/common/scripts/cronExecutor_MergeBatchWithLock_hdfs.sh'
      ```
    - If they are already running wait for them to stop.

### Migrate traffic between DR/PR

1. Start `prodrestib` Wildfly instances at both edge nodes of the other site using this [procedure](manage_wildfly.md#start-a-wildfly-instance-prodrestib).

2. Start `prodreston` Wildfly instances at both edge nodes of the other site using this [procedure](manage_wildfly.md#start-a-wildfly-instance-prodreston).

3. Ask for a mno Network administrator to make a call.
   
4. Ask them to enable the new servers (mention the Loadbalancer IPs and the IP you want them to enable as explained [here](manage_wildfly.md#consolidated-network-information)).
   
5. Check logs for both Wildfly instances at both servers to ensure everything works.
   
6. When you are certain everything is OK, ask the mno Network administrators to disable the prexisting servers (mention the Loadbalancer IPs and the IP you want them to disable).
   
7. From the access logs of the prexisting Wildfly instances check that no traffic is received. 
   
8. Stop these Wildfly instances as described in the procedures [here](manage_wildfly.md#stop-a-wildfly-instance-prodrestib) and [here](manage_wildfly.md#stop-a-wildfly-instance-prodreston).

### Migrate UC4 flows between PR/DR

1. Login to the edge servers of the active and passive site using your personal account and become `root`.

2. Stop UC4 agent at the edge nodes of the active site.
   
  ``` bash
  systemctl stop uc4agent
  ```

3. Start service for UC4 agent at the edge servers of the passive site.

  ``` bash
  systemctl start uc4agent
  ```

4. Add entries for last successful execution of IBank DataWarehouse at the edge servers of the passive site.

  ``` bash
  sudo -u PRODUSER /opt/ingestion/PRODUSER/datawarehouse-ibank/insert_rows_dwh_monitoring.sh <date> 
  # Previous day date (YYYYMMdd), unless Sunday or Monday
  # If Sunday or Monday enter the date of last Friday
  ```

5. Migrate the creation of trigger files for external jobs

  - On the active site:

    ``` bash
    vi /opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh
    # Comment the followin lines along with the assosiated checks
    # touch /home/bank_central_mno_gr/datawarehouse_status/IBANK_SA_`date '+%Y%m%d'`.READY
    # touch /opt/applications/landing_zone/PRODUSER/triggers/IBANK_SA_`date '+%Y%m%d'`.READY
    ```  
  - On the passive site:

    ``` bash
    vi /opt/ingestion/PRODREST/historical/ibank_histMigrate_aggr_MergeBatchWithLock_STABLE_v2.sh
    # Uncomment the followin lines along with the assosiated checks
    # touch /home/bank_central_mno_gr/datawarehouse_status/IBANK_SA_`date '+%Y%m%d'`.READY
    # touch /opt/applications/landing_zone/PRODUSER/triggers/IBANK_SA_`date '+%Y%m%d'`.READY
    ```  
