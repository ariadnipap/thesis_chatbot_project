# TeMIP

- [TeMIP](#temip)
  - [Overview](#overview)
  - [Flows](#flows)
    - [Main Application](#main-application)
    - [Initialization/Synchronization](#initializationsynchronization)
    - [Move Kudu to Impala](#move-kudu-to-impala)
    - [Alert Mail](#alert-mail)
  - [Manual Actions](#manual-actions)
    - [Restart Wildfly Server](#restart-wildfly-server)
    - [Load Terminated Alarms from TeMIP Oracle Database In case of data loss](#load-terminated-alarms-from-temip-oracle-database-in-case-of-data-loss)
  - [TeMIP Wildfly Server](#temip-wildfly-server)
    - [Logging](#logging)
      - [Change logging level](#change-logging-level)
  - [Useful Links](#useful-links)

## Overview

The `abc TeMIP alarms live feed to BigStreamer` application is a Java application hosted on a Wildfly application server. The objective of the application is to receive and store (in near real time) the TeMIP alarms (from specific TeMIP Operation Contexts) into the BigStreamer™ ecosystem. The `Apache Kudu` storage engine was selected in order to achieve near real time CRUD operations (Create, Read, Update, Delete). The `Apache Impala` is used for extended data retention (6 months). The `Apache Oozie` scheduler  is used in order to automatically run the necessary scripts.

- **Ndef:** All the needed **passwords** can be found [**here**](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/devpasswd.kdbx).

## Flows

The `TeMIP Flow` consists of 4 components/flows:
1. Initialization/Synchronization flow
1. Main Application flow
1. Move Kudu to Impala flow
1. Alert Mail flow

### Main Application

The `Main Application Flow` contains our `TeMIP application` deployed to the `Wildfly Server` which receives the TeMIP alarms and stores them into Kudu tables.

``` mermaid
  flowchart TD
  A[TeMIP Server] 
  B[Wildfly Server]
  A --> |Sends TeMIP alarms| B
  B --> |Stores TeMIP alarms| D[(Kudu Storage Engine)]
  D --- E[Kudu: temip.temip_kudu_active_alarms]
  D --- Z[Kudu: temip.temip_kudu_terminated_alarms]
  D --- K[Kudu: temip.temip_kudu_historic_events]
  style A fill: #45b39d
```

- **TeMIP Server**
  - **Host:** `999.999.999.999`
  - **Port:** `7180`
- **Wildfly Server**
  - **Servers:**
    - `temip1 (999.999.999.999)` Standby Server
    - `temip2 (999.999.999.999)` Active Server
  - **User:** `temip`
  - **Installation Path:** `/opt/wf_cdef_temip/`
  - **Deployments Path:** `/opt/wf_cdef_temip/standalone/deployments`
  - **Application Logs:** `/opt/wf_cdef_temip/standalone/log/server.log`
  - **Access Logs:** `/opt/wf_cdef_temip/standalone/log/access.log`
  - **Configuration:** `/opt/wf_cdef_temip/standalone/configuration/BigStreamer/config/`
    - **File:** `temip.properties`

**Alerts:**

- **Mail executed by [Alert Mail](#alert-mail)**
  - **Subject:** `"[ Temip ] No alarms available."`
  - **Body:** `"There are no Temip alarms  available for the last hour. Corrective action may be needed."`

**Troubleshooting Steps:**

1. Check `logs` (application and access) with `temip-tailog` for any `ERROR` message that can occur.  
If TeMIP Server is running correctly, we should see lines like the following:  
`INFO [com.jkl.bigstreamer.abc.temip.core.service.TemipService] (default task-173) Counter= 3064020, handle= 968, batchName= batch_2, timesRestartedFromLastSync= 1, aoExtractDataList size= 1`
1. Check if `TeMIP Server` is up by executing `ping 999.999.999.999`.
1. Contact a `TeMIP admin` to see if there are any server side related issues

### Initialization/Synchronization

The `Initialization/Synchronization Flow` consists of an OOZIE Coordinator called `TeMIP_Synchronization_CO`. The coordinator is responsible for establishing the **connection** and **communication** of the `Wildfly Server` (containing our TeMIP Application) with the `TeMIP Server`.

Every time the `Main Application` is successfully deployed to `Wildfly Server` or gets restarted, this `coordinator` **must be run manually** to initiate the above procedure, it does not happen automatically. If the `Wildfly Server` is up and running, the `coordinator` executes on specific days of every month to perform maintenance tasks.

``` mermaid
  flowchart TD
  A[OOZIE Server] -->|SHELL Action as user temip| B[un-vip.bigdata.abc.gr <br> User: temip]
  B -->|REST message protocol| C[Main Application]
  C <--> |SOAP message protocol| D[TeMIP Server]
  style C fill: #45b39d
```

- **Oozie Coordinator**
  - **Hue:** `https://un-vip.bigdata.abc.gr:8888`
  - **User:** `temip`
  - **Coordinator:** `TeMIP_Synchronization_CO`
    - **Execution:** `2,7,12,17,22,27 of every month at 03:00 local time`
    - **Approximate Duration:** `45 minutes`
    - **Workflow:** `TeMIP_Synchronization_WF`
      - **Master Script:** `hdfs:/user/temip/100.TeMIP_Synchronization_Oozie_Main.sh`
      - **Remdef Script:** `un-vip:/shared/abc/temip_oozie_production_scripts/101.temip_synchronization_Main.sh`
      - **Server:** `un-vip.bigdata.abc.gr`
      - **SSH User:** `temip`
      - **Logs:** `un-vip:/shared/abc/temip_oozie_production_scripts/log/102.temip_synchronization.$(date '+%Y%m%d').log`

**Alerts:**

- **Not Monitored**

**Troubleshooting Steps:**

1. Check logs for any errors
1. If workflow `TeMIP_Synchronization_WF` has been run manually, login to `Hue` with `temip` user `after 45 minutes` and execute the following `impala query` editor: `select * from temip.temip_kudu_configs`.  
It should return `15 rows`. If not, re run the `TeMIP_Synchronization_WF` workflow

### Move Kudu to Impala

The `Move Kudu to Impala` flow consists of a coordinator called `TeMIP_kudu_2_Impala_CO` which executes once a day and is responsible for moving the alarms from kudu to the equivalent impala table.

``` mermaid
 flowchart TD
  A[OOZIE Job] 
  Z[Kudu: temip.temip_kudu_terminated_alarms]
  K[Kudu: temip.temip_kudu_historic_events]
  A --> Z
  A --> K
  Z --> |Move older alarms to impala|H[Impala: temip.temip_impala_terminated_alarms]
  K --> |Move older events to impala|L[Impala: temip.temip_impala_historic_events]
```

- **Oozie Coordinator**
  - **Hue:** `https://un-vip.bigdata.abc.gr:8888`
  - **User:** `temip`
  - **Coordinator:** `TeMIP_kudu_2_Impala_CO`
    - **Execution:** `everyday at 06:00 local time`
    - **Approximate Duration:** `15 minutes`
    - **Workflow:** `TeMIP_kudu_2_Impala_WF`
      - **Script:** `hdfs:/user/temip/temip_kudu_to_impala.sh`
      - **Logs:** `Through Oozie Job in HUE`

**Alerts:**

- **Not Monitored**

**Troubleshooting Steps:**

1. Check that workflow `TeMIP_kudu_2_Impala_WF` runs successfully. This can be done through accessing `Hue` with `temip` user and selecting `Jobs`. Then filter the jobs with `user:temip` and look for a `job` with the below properties:
    - **Name:**  `oozie:launcher:T=shell:W=temip_kudu_to_impala:A=shell-661a:*`
    - **Type:** `Oozie Launcher`
    - **Execution Time:** `06:00 AM`

    Select the desired shell execution, view its logs and search for any ERRORS.
1. After the root cause of the problem has been identified, re-rerun the failed execution. This can be done through accessing `Hue` with `temip` user.

### Alert Mail

The `Alert Mail` flow consists of a coordinator called `TeMIP_Alert_Mail_CO` which runs every hour and checks if the application receives any alarms from the TeMIP Server. The `TeMIP Server` sends alarms continuously. If in the last hour, the application has not detected any new alarms, an email is sent to jkl Engineers to inform that there might be a issue. The check is performed by comparing the number of alarms from the previous execution stored in `temip.temip_alert_table` table with the current one.

``` mermaid
 flowchart TD
  A[OOZIE Server] -->|SHELL Action as user temip| B[un-vip.bigdata.abc.gr <br> User: temip]
  B --> C[201.temip_alert_mechanism_Main.sh]
```

- **Oozie Scheduler**
  - **Hue:** `https://un-vip.bigdata.abc.gr:8888`
  - **User:** `temip`
  - **Coordinator:** `TeMIP_Alert_Mail_CO`
    - **Execution:** `every hour`
    - **Workflow:** `TeMIP_Alert_Mail_WF`
      - **Master Script:** `hdfs:/user/temip/200.TeMIP_Alert_Mail_Oozie_Main.sh`
      - **Remdef Script:** `un-vip/shared/abc/temip_oozie_production_scripts/201.temip_alert_mechanism_Main.sh`
      - **Server:** `un2.bigdata.abc.gr`
      - **SSH User:** `temip`
      - **Logs:** `un-vip:/shared/abc/temip_oozie_production_scripts/log/202.temip_alert_mechanism.$(date '+%Y%m%d').log`

**Alerts:**

- **Not Monitored**

**Troubleshooting Steps:**

1. Check for any failed executions. This can be done through accessing `Hue` with `temip` user
1. Check for any cluster related problems during the failed execution.

## Manual Actions

### Restart Wildfly Server
---

**_Ndef:_** TEMIP runs only in one node. Second node is in standby mode.

1. **Only if requested by TeMip Administrators** In `Hue` with `temip` user, clear table `temip.temip_kudu_active_alarms` by executing `delete from temip.temip_kudu_active_alarms;`
1. `Shutdown Wildfly Server`
    1. Login as `temip` user in `temip2`.
    1. Execute `/bin/bash` and then run `temip-stop` to stop wildfly and check logs with `temip-tailog`.
    1. Suspend the temip Coordinators (`Hue` with `temip` user):
        - `TeMIP_kudu_2_Impala_CO`
        - `TeMIP_Synchronization_CO`
        - `TeMIP_Alert_Mail_CO`
    1. Clear table `temip.temip_kudu_active_alarms` by executing `delete from temip.temip_kudu_active_alarms;` in `Hue` as `temip` user 

1. `Startup Wildfly Server`
    1. Login as `temip` user in `temip2`.
    1. Start wildfly by executing `/bin/bash` and then running `temip-start` and check logs with `temip-tailog`.
    1. Resume the three temip coordinators (`Hue` with `temip` user):
        - `TeMIP_kudu_2_Impala_CO`
        - `TeMIP_Synchronization_CO`
        - `TeMIP_Alert_Mail_CO`
    1. Workflows:
        - The two workflows `TeMIP_kudu_2_Impala_WF` and `TeMIP_Alert_Mail_WF` should run automatically when oozie scheduler detects that it was suspended.
        - The third workflow `TeMIP_Synchronization_WF` should be run manually. Specifically, `login` as `temip` to `Hue` and run manually with no parameters. Make sure that it will not also be executed by the corresponding coordinator.
    1. At `HUE` with `temip` user, open the impala editor and execute the following command in order to refresh e-mail alert script:  
      `insert overwrite temip.temip_alert_table values(1);`

1. `Sanity Checks`

    1. Login as `temip` user in `temip2`
    1. Check `logs` with `temip-tailog` and search for any errors.
    1. After `45 minutes`, login to `Hue` with `temip` user and execute the following impala query editor:  
    `select * from temip.temip_kudu_configs`  
      It should return 15 rows. If not, `re run` the `TeMIP_Synchronization_WF` workflow.
    1. Login to `Hue` with `temip` and perform the below impala queries with a temip admin (Ioanna Bekiari) in order to established if everything is running okay. If the results are the same or really similar, the synchronization is considered successful.

        ``` sql
        select count(*) from temip_kudu_active_alarms where operation_context like '%ENM_BASEBAND%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%ERICOSS2G%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%ERICOSS-LTE%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%NOKIA3G%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%.ATHENS-OC%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%NNM_FIXED%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%U2000-OC%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%1350OMS%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%HUAWEI_IMS%';
        select count(*) from temip_kudu_active_alarms where operation_context like '%AUMS-OC%';
        select count(*) from temip_kudu_active_alarms where operation_context like '.def.A5529.A5520_AMS-OC';
        select count(*) from temip_kudu_active_alarms where operation_context like '%2000_DSLAM%';
        ```

### Load Terminated Alarms from TeMIP Oracle Database In case of data loss
---

In case there is a loss of alarms for any reason, eg our application or TeMIP outage, we may be asked to load historical data directly from TeMIP Oracle Database into our terminated alarms table. In order to start this operation we must wait for some days, so that all alarms are transferred to the Oracle table. Whole procedure is described in detail below:

1. Wait `7 days` from the day you want to `re-load` in order for terminated alarms to be refreshed in Oracle table.

1. Connect as `temip` in `un2` and run `ping 999.999.999.999`, in order to see if `Temip Server` is up and running.

1. From impala shell `secimp`(as `temip` in `un2`) or `Hue`(as `temip`):

	1. Check missing partitions in `temip.temip_kudu_terminated_alarms` and `temip.temip_impala_terminated_alarm` by running  
  `select count(*), par_dt from <database>.<table> where par_dt='<partition>' group by par_dt;` on both tables.  
		We receive TeMIP alarms every day. So if there are general ERRORS(logs) or we have partitions containing less alarms than usual(eg. count), it suggests that there might be problems with the TeMIP server or our application and in need of investigating.

	1. Delete existing wrong partitions that overlap with the required interval, either from kudu table `temip.temip_kudu_terminated_alarms` or from impala table `temip.temip_impala_terminated_alarms`.
		- If wrong partitions are contained in kudu table (only 10 most recent days are in kudu), do:  
`ALTER table temip.temip_kudu_terminated_alarms DROP IF EXISTS RANGE PARTITION 'v1'<= values < 'v2';`,   
where v1 and v2 the required interval.

		- If wrong partitions are contained in impala table (10 days past the current date), do:  
`ALTER table temip.temip_impala_terminated_alarms DROP IF EXISTS PARTITION (par_dt='v');`,   
where v is the wrong partition.

	1. In order to not tranfer again old data that have remained, run `truncate table temip.temipdb_term_alarms_load_par;`.

1. As `temip` in `un2` Run the script with arguments
    ``` bash
    sh /usr/icom/scripts/Sqoop_Oracle_HDFS_Impala_Load_TeMIP_v832.sh "temipaharchi.alarmobject0" identifier 30 <current-pardt> "terminationtimestamp>='v1' and terminationtimestamp<'v2'"
    ```
    - **current-pardt:** is the `today` par_dt, the day the script is run. Format `YYYYMMDD`. It has no significant value to the internal process.
    - **v1, v2:** Use values for `terminationtimestamp` that are between the start and end of the interval you want to load from Oracle. Format `01-MAY-22`.

    Example for day 20220501:
    ``` bash
    sh /usr/icom/scripts/Sqoop_Oracle_HDFS_Impala_Load_TeMIP_v832.sh "temipaharchi.alarmobject0" identifier 30 20230104 "terminationtimestamp>='01-MAY-22' and terminationtimestamp<'02-MAY-22'"
    ```
    The data will be **loaded** into table `temip.temipdb_term_alarms_load_par`.

1. From impala shell `secimp`(as `temip` in `un2`) or `Hue`(as `temip`):

    1. Refresh the staging table in the impala shell:  
      `refresh temip.temipdb_term_alarms_load_par;`

    1. Run the following sql command, which transfers automatically all data to the right partition (par_dt) of temip.temip_impala_terminated_alarms:

        ``` sql
        insert overwrite temip.temip_impala_terminated_alarms partition (par_dt)
        select concat('OPERATION_CONTEXT ',split_part(upper(ocname),':',2),' ALARM OBJECT ', identifier) outentityspec,
        null last_Modification_Timestamp,
        split_part(upper(ocname),':',2) operation_context,
        cast(identifier as bigint) identifier,
        "Terminated-Oracle" state,
        "Closed" problem_status,
        case when clearancereportflag = "1" then true else false end clearance_report_flag,
        acknowledgementuseride as acknowledgement_user_identifier,
        handledby as handled_by,
        closedby as closed_by,
        handleduseridentifier as handled_user_identifier,
        releaseuseridentifier as release_user_identifier,
        closeuseridentifier as close_user_identifier,
        terminationuseridentif as termination_user_identifier,
        acknowledgementtimesta as acknowledgement_time_stamp,
        handletimestamp as handle_time_stamp,
        closetimestamp as close_time_stamp,
        terminationtimestamp as termination_time_stamp,
        releasetimestamp as release_time_stamp,
        null automatic_terminate_on_close,
        creationtimestamp as creation_timestamp,
        archivetimestamp as archive_time_stamp,
        clearancetimestamp as clearance_time_stamp,
        null previous_state,
        managedobject as managed_object,
        targetentities as target_entities,
        --targetentities60512 as target_entities,
        alarmtype as alarm_type,
        eventtime as event_time,
        probablecause as probable_cause,
        securityalarmcause as security_alarm_cause,
        specificproblems as specific_problems,
        --specificproblems (id)-8eloume to join kai edw,
        null backed_up_status,
        backupobject as backup_object,
        trendindication as trend_indication,
        thresholdinfo as threshold_info,
        cast(notificationidentifier as bigint) notification_identifier,
        correlnotifinfo as correl_notif_info,
        monitoredattributes as monitored_attributes,
        proposedrepairactions as proposed_repair_actions,
        null additional_information,
        domain as domain,
        securityalarmdetector as security_Alarm_Detector,
        null service_User,
        null service_Provider,
        ocname as oc_Name,
        cast(parentalarmobject as bigint) parent_alarm_object,
        null severity_changed_time_stamp,
        alarmcomment as alarm_comment,
        agentalarmidentifier as agent_alarm_identifier,
        agententity as agent_entity,
        perceivedseverity as perceived_Severity,
        additionaltext as additional_Text,
        alarmobjectoperatorno as alarm_Object_Operator_Ndef,
        originalseverity as original_Severity,
        originaleventtime as original_Event_Time,
        0 useridentifier,
        usertext as user_Text,
        cast(satotal as bigint) sa_total,
        null deleted,
        from_timestamp(to_timestamp(terminationtimestamp,'yyyy-MM-dd HH:mm:ss'),'yyyyMMdd') as par_dt
        --,*
        from temip.temipdb_term_alarms_load_par a;
        ```

        **Ndef:** There are comments that might affect the query if not handled carefully. 

    1. Check if data transferred successfully by running the command below and comparing the result with the number of retrieved records in the logs produced by the script.  

      ``` sql
      SELECT par_dt, count(*) FROM temip.temip_impala_terminated_alarms where par_dt > 'v';
      Eg. Logs: INFO mapreduce.ImportJobBase: Retrieved 1113488 records.  
      +----------+  
      | count(*) |  
      +----------+  
      | 1113488  |  
      +----------+  
      ```

## TeMIP Wildfly Server

In order to change the `logging level` of any of the `categories` of the `TeMIP Wildfly Server` access the `WildFly Management`.

### Logging

In order to change the `logging level` of any of the categories of the `TeMIP Wildfly Server` access the `WildFly Management`.

- [Home URL](https://999.999.999.999:8888/)
- **User:** `admin`
- **Password:** [abc-syspasswd.kdbx](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/abc-syspasswd.kdbx)

#### Change logging level

1. Login to the `WildFly Management` by following the [home url](https://999.999.999.999:10213/console/App.html#home), select `Configuration` ~> `Subsystems` ~> `Logging` and select `View`.
1. Select `LOG CATEGORIES`
1. From the table select the `category` you desire to change its **logging level** e.g. com.jkl.bigstreamer.abc.temip is our main TeMIP App.
1. Press the `Edit` option below the table
1. Select the desired `Level` between the given options. 
1. Click `Save`
1. Ssh from `un2` with `temip` to `temip1` or `temip2` with `temip` user and check that in the file `/opt/wf_cdef_temip/standalone/configuration/standalone-full.xml` the level of the previously configured logger has changed successfully. It should be configured **automatically**. 

## Useful Links

- [TeMIP Dir](https://metis.ghi.com/obss/bigdata/abc/temip)
- [TeMIP Application Deployment](https://metis.ghi.com/obss/bigdata/abc/temip/temip-devops/-/wikis/Application-Deployment)
- [TeMIP Wiki](https://metis.ghi.com/obss/bigdata/abc/temip/temip-devops/-/wikis/home)
