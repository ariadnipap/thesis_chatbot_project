# TeMIP

## 1. Overview

The `abc TeMIP alarms live feed to BigStreamer` application is a Java application hosted on a Wildfly application server. The objective of the application is to receive and store (in near real time) the TeMIP alarms (from specific TeMIP Operation Contexts) into the BigStreamer™ ecosystem. The `Apache Kudu` storage engine was selected in order to achieve near real time CRUD operations (Create, Read, Update, Delete). The `Apache Impala` is used for extended data retention (6 months). The `Apache Oozie` scheduler  is used in order to automatically run the necessary scripts.

- **Ndef:** All the needed **passwords** can be found [**here**](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/devpasswd.kdbx).

## 2. Installation & Configuration
### Scripts & Configuration
- Install dependencies
- Configure Oozie

## 3. Data Processing

### Flows

The `TeMIP Flow` consists of 4 components/flows:
1. Initialization/Synchronization flow
1. Main Application flow
1. Move Kudu to Impala flow
1. Alert Mail flow

#### Main Application

The `Main Application Flow` contains our `TeMIP application` deployed to the `Wildfly Server` which receives the TeMIP alarms and stores them into Kudu tables.

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
- **Mail executed by Alert Mail**
  - **Subject:** `"[ Temip ] No alarms available."`
  - **Body:** `"There are no Temip alarms available for the last hour. Corrective action may be needed."`

**Troubleshooting Steps:**
1. Check `logs` (application and access) with `temip-tailog` for any `ERROR` message.
2. Check if `TeMIP Server` is up by executing `ping 999.999.999.999`.
3. Contact a `TeMIP admin` to see if there are any server-side related issues.

#### Move Kudu to Impala

The `Move Kudu to Impala` flow consists of a coordinator called `TeMIP_kudu_2_Impala_CO` which executes once a day and is responsible for moving the alarms from kudu to the equivalent impala table.

- **Oozie Coordinator**
  - **Hue:** `https://un-vip.bigdata.abc.gr:8888`
  - **User:** `temip`
  - **Coordinator:** `TeMIP_kudu_2_Impala_CO`
    - **Execution:** `every day at 06:00 local time`
    - **Approximate Duration:** `15 minutes`
    - **Workflow:** `TeMIP_kudu_2_Impala_WF`
      - **Script:** `hdfs:/user/temip/temip_kudu_to_impala.sh`
      - **Logs:** `Through Oozie Job in HUE`

**Alerts:**
- **Not Monitored**

**Troubleshooting Steps:**
1. Check that workflow `TeMIP_kudu_2_Impala_WF` runs successfully.
2. After identifying the root cause of the problem, re-run the failed execution.

## 4. Monitoring & Debugging
### Logs
- Logs stored in `/var/logs`

### TeMIP Wildfly Server

In order to change the `logging level` of any of the `categories` of the `TeMIP Wildfly Server` access the `WildFly Management`.

- [Home URL](https://999.999.999.999:8888/)
- **User:** `admin`
- **Password:** [abc-syspasswd.kdbx](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/abc-syspasswd.kdbx)

#### Change logging level

1. Login to the `WildFly Management` by following the [home url](https://999.999.999.999:10213/console/App.html#home).
2. Select `Configuration` ~> `Subsystems` ~> `Logging` and select `View`.
3. Select `LOG CATEGORIES`.
4. From the table select the `category` you desire to change its **logging level**.
5. Press the `Edit` option below the table.
6. Select the desired `Level` between the given options.
7. Click `Save`.
8. SSH from `un2` with `temip` to `temip1` or `temip2` and check `/opt/wf_cdef_temip/standalone/configuration/standalone-full.xml`.

## 5. Troubleshooting
### Restart Wildfly Server
1. **Only if requested by TeMip Administrators** In `Hue` with `temip` user, clear table `temip.temip_kudu_active_alarms`.
2. Shutdown Wildfly Server:
    - Login as `temip` user in `temip2`.
    - Execute `/bin/bash` and run `temip-stop` to stop wildfly.
3. Resume the three TeMIP coordinators (`Hue` with `temip` user):
    - `TeMIP_kudu_2_Impala_CO`
    - `TeMIP_Synchronization_CO`
    - `TeMIP_Alert_Mail_CO`
4. Perform `Sanity Checks`:
    - Check logs with `temip-tailog`.
    - After 45 minutes, run `select * from temip.temip_kudu_configs` in Hue.

### Load Terminated Alarms from TeMIP Oracle Database In case of data loss
1. Wait `7 days` from the day you want to `re-load` to allow terminated alarms to refresh in Oracle.
2. Connect as `temip` in `un2` and run `ping 999.999.999.999`.
3. From impala shell `secimp` or `Hue` (as `temip`), check missing partitions.
4. Delete existing wrong partitions.
5. Run:
   ```bash
   sh /usr/icom/scripts/Sqoop_Oracle_HDFS_Impala_Load_TeMIP_v832.sh "temipaharchi.alarmobject0" identifier 30 20230104 "terminationtimestamp>='01-MAY-22' and terminationtimestamp<'02-MAY-22'"

    Refresh the staging table:

refresh temip.temipdb_term_alarms_load_par;

Run the following SQL to insert the data:

insert overwrite temip.temip_impala_terminated_alarms partition (par_dt)
select outentityspec, state, problem_status, creation_timestamp, termination_time_stamp, par_dt
from temip.temipdb_term_alarms_load_par;

Check if data transferred successfully.

## 6. Data Validation & Checks

## 7. Miscellaneous Notes

## Useful Links

- [TeMIP Dir](https://metis.ghi.com/obss/bigdata/abc/temip)
- [TeMIP Application Deployment](https://metis.ghi.com/obss/bigdata/abc/temip/temip-devops/-/wikis/Application-Deployment)
- [TeMIP Wiki](https://metis.ghi.com/obss/bigdata/abc/temip/temip-devops/-/wikis/home)
