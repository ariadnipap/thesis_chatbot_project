---
title: Prometheus Oracle to Hive ETL Flow
system: BigStreamer
component: Prometheus
job_name: Prometheus-Import-Workflow
source_system: Oracle
source_tables:
  - DWSRC.DWH22
destination_system: Hive
destination_tables:
  - prometheus.dwh22
schedule: daily at 06:30 UTC
coordinator: Prometheus-Coordinator
workflow: Prometheus-Import-Workflow
script_path: /user/prometheus/flows
monitoring_table: monitoring.jobstatus
owner: prometheus
tags:
  - Prometheus
  - Oracle to Hive
  - ETL
  - BigStreamer
  - Monitoring
  - Oozie
  - Impala
  - Workflow Troubleshooting
  - Partition Drop
  - Grafana
---
# Prometheus
This document describes the Prometheus ETL flow that extracts data from Oracle table DWSRC.DWH22 into the Hive table prometheus.dwh22 using a daily Oozie workflow. It includes scheduling details, partition management, and troubleshooting guidelines in case of failures.
## Useful Links
References to internal documentation related to infrastructure and monitoring of the Prometheus ETL flow.
[Infrastructure](https://metis.ghi.com/obss/bigdata/abc/etl/prometheus/prometheus-devops/-/wikis/Infastructure)  
[Monitoring](https://metis.ghi.com/obss/bigdata/abc/etl/prometheus/prometheus-devops/-/wikis/home#monitoring)  
## Oozie workflow / ETL Flow: Oracle to Hive
Description of the Oracle-to-Hive import flow, configuration details, and how to monitor and troubleshoot job execution.
``` mermaid
  graph TD
    A[Oracle DB table DWSRC.DWH22  <br> via Port Forward 999.999.999.999:6634] -->|Sqoop Import| B[HDFS Staging Directory]
    B -->|Hive Load| C[Hive: prometheus.dwh22]
    C -->|Impala Refresh| D[Impala: prometheus.dwh22]
```
Runs every day at `06:30 AM UTC`
**User**: `prometheus`  
**Coordinator**: `Prometheus-Coordinator`  
**Workflow**: `Prometheus-Import-Workflow`  
**Source Database**:  
- **Host**: `999.999.999.999`  
- **Port**: `1521`  
- **SID**: `A7`
- **User**: `bigstreamer`  
**Target Table**: `prometheus.dwh22`  
**HDFS Installation Directory**: `/user/prometheus/flows`  
**HDFS Staging Directory**: `/ez/warehouse/prometheus.db/tmp_sqoop_jobs/`
**Alerts**:
- Mail with subject: `Prometheus Flow failed`
**Troubleshooting Steps**:
- Check messages written to Monitoring App
    - Check monitoring app for successful executions:  
        - From `un2` with personal account:
        - `curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=PROMETHEUS$status=SUCCESS&operativePartition=<timestamp e.g.:20220518>'`
    - Check monitoring app for failed executions:  
        - From `un2` with personal account:
        - `curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/api/jobstatus/find?application=PROMETHEUS$status=FAILED&operativePartition=<timestamp e.g.:20220518>'`
    - Get all the available fields [here](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/API-Functional-Spec#fields)
    - Grafana link: `https://unc1.bigdata.abc.gr:3000/d/PcKYyfTVz/prometheus-dashboard?orgId=1&from=now-2d&to=now`
- Check if partition is loaded:
  From `Hue` as `prometheus` in `Impala Editor`:
  ``` sql
  SHOW PARTITIONS prometheus.dwh22;
  SELECT COUNT(*) FROM prometheus.dwh22 WHERE par_dt='<par_dt>';
  ```
- Check logs for failed steps:  
  From `Hue` as `prometheus` in `Workflows`:
  - Search for `Prometheus-Import-Workflow` and filter for failed
  - Go to logs and check both stdout and stderr
- In case a partition has partially been inserted into the final table `prometheus.dwh22` and the error that caused the failure has been resolved:
  From `Hue` as `prometheus` in `Impala Editor`:
    ``` sql
    ALTER TABLE prometheus.dwh22 DROP IF EXISTS PARTITION (par_dt='<par_dt>');
    ```
  - For the previous day:
    From `Hue` as `prometheus` in `Workflows`:
    - Search for `Prometheus-Import-Workflow` and filter for `failed`
    - Re-run it
  - For the previous day:
    From `Hue` as `prometheus` in `Workflows`:
    - Search for `Prometheus-Import-Workflow` and filter for `failed`
    - Re-run it
  - For partitions older than yesterday:
    From `Hue` as `prometheus` in `File Browser`:
    - Edit `/user/prometheus/flows/config/settings_prod.ini` and set `days_back` to the number of days back needed to reach the partition
    From `Hue` as `prometheus` in `Workflows`:
    - Search for `Prometheus-Import-Workflow` and filter for `failed`
    - Re-run it
    From `Hue` as `prometheus` in `File Browser`:
    - Edit `/user/prometheus/flows/config/settings_prod.ini` and restore `days_back` to `1`