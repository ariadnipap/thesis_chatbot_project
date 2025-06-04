---
title: "Execute Cube Indicators via Terminal"
description: "Instructions for manually executing the Cube Indicators Spark job from terminal on un1.bigdata.abc.gr, including how to pull the latest script, modify execution date, and run the submit script."
tags:
  - cube indicators
  - spark job
  - pyspark
  - hdfs
  - brond
  - manual execution
  - terminal
  - big data
  - intra
---
# Execute Cube Indicators via Terminal
This guide explains how to manually run the Cube Indicators Spark job for missing dates from the terminal. It includes pulling the latest script from HDFS, updating the execution date, and submitting the job.
1. SSH into `un1.bigdata.abc.gr` and switch to the `intra` user:
```bash
ssh un1.bigdata.abc.gr
sudo -i -u intra
```
2. Navigate to the working directory:
```bash
cd projects/cube_ind
```
3. Remove the old PySpark script:
```bash
rm Indicators_Spark_Job.py
```
4. Authenticate with Kerberos and fetch the updated script from HDFS:
```bash
kinit -kt /home/intra/intra.keytab intra
hdfs dfs -get /user/intra/cube/Indicators_Spark_Job.py
```
6. Edit submit script to change execution date. The execution date should be 2 days after the missing data date.
For example, to load data for 2021-01-01, set the execution date to 2021-01-03.
```bash
vim run_cube.sh
```
Update the relevant line:
```bash
...verhead=4096 Indicators_Spark_Job.py <date> brond.dsl_s...
```
7. Run the Spark job:
```bash
./run_cube.sh
```
---
tags:
  - cube indicators
  - pyspark
  - spark job
  - brond
  - manual data load
  - hdfs
  - intra
---