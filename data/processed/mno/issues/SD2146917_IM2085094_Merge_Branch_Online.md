---
title: Online_Ingestion MergeBatch Failure on DR Due to Sentry Permission Check Failure
description: The MergeBatch job for Online_Ingestion on the DR site failed due to a Permission Denied error in HDFS caused by Sentry failing to validate permissions during MySQL unavailability; issue resolved by rerunning the job manually and reporting to Graphite.
tags:
  - mno
  - bigstreamer
  - online_ingestion
  - merge batch
  - spark
  - grafana
  - hdfs
  - sentry
  - mysql
  - graphite
  - dr site
  - batch failure
  - permission denied
  - sd2146917
  - im1996192
  - im2083185
last_updated: 2025-05-01
author: ilpap
context:
  issue_id: SD2146917-IM1996192-IM2083185
  system: mno BigStreamer DR Site
  root_cause: Sentry failed to verify permissions due to temporary MySQL unavailability, resulting in HDFS Permission Denied error during MergeBatch job
  resolution_summary: Verified that target par_dt had no records, manually reran the MergeBatch script, and executed Report to Graphite
  impacted_component: Online_Ingestion MergeBatch
  hdfs_dir_issue: true
  permissions_check_failed: true
---
# mno - BigStreamer - SD2146917-IM1996192-IM2083185 - Online_Ingestion MergeBatch Failure on DR
## Description
We have the following alert msg on Grafana:
```
[DR][IBANK] Online_Ingestion MergeBatch Failed
```
## Actions Taken
Login to `dr1edge01` with your acount
```bash
su - PRODREST
```
We look at the script log:
```bash
/var/log/ingestion/PRODREST/online/logonExecutor_OnlineBatch_full.log
```
The problem was :
`Permission Denied on hdfs dir. Due to unavailability of mysql it could not check the sentry permissions which are certain`
The main problem was due to some tasks running `deν` there was communication with the server to get the correct Permission.
we will have to rerun the script manually. Before running the script we will see if there are records in the table for each `par_dt`.
Ensure that no records are present in prod_trlog_online.service_audit (eg 23_03_2023)
```bash
impala-shell -k --ssl -i ${HOSTNAME/01/} -q "select count(*) from prod_trlog_online.service_audit where par_dt='20230223';"
```
If there is no record for the above `par_dt` then we run the script again.
```bash
/opt/ingestion/PRODREST/common/scripts/cronExecutor_MergeBatchWithLock_hdfs_STABLE.sh /user/PRODREST/lock/PROD_Online_MergeBatch LOCK_ONLINE_PROD_BATCH_MERGE_TRANS /opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_batch_cluster_mno_STABLE.sh PROD_Online_MergeBatch /opt/ingestion/PRODREST/online/lock/ FULL 1800 "`date --date='-1 day' '+%Y-%m-%d 00:00:00'`" "`date '+%Y-%m-%d 00:00:00'`" >> /var/log/ingestion/PRODREST/online/log/cronExecutor_onlineBatch_full.log 2>&1 &
```
Because it had failed for the previous day, we ran the script for the previous day.
The script ran for over 4 hours.
After the above script successfully executed we ran the step [Report Start to Graphite](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/mno/BigStreamer/supportDocuments/applicationFlows/online.md#report-stats-to-graphite)
## Root Cause
The MergeBatch job failed due to an HDFS permission denied error, which was caused by Sentry being unable to validate access rules due to MySQL unavailability. This prevented Spark from accessing required directories during job execution.