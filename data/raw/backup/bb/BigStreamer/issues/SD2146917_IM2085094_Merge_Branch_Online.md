# mno - BigStreamer - SD2146917-IM1996192-IM2083185 [DR][IBANK] Application : Online_Ingestion MergeBatch Failed

<b>Description:</b>

We have the following alert msg on Grafana.
[DR][IBANK] Online_Ingestion MergeBatch Failed

<b>Actions Taken:</b>

Login to `dr1edge01` with your acount
```
su - PRODREST
```
We look at the script log:
```
/var/log/ingestion/PRODREST/online/logonExecutor_OnlineBatch_full.log
```
The problem was :

`Permission Denied on hdfs dir. Due to unavailability of mysql it could not check the sentry permissions which are certain`

The main problem was due to some tasks running `deν` there was communication with the server to get the correct Permission.

we will have to rerun the script manually. Before running the script we will see if there are records in the table for each `par_dt`

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
