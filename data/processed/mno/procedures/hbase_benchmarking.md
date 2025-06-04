---
title: Benchmarking HBase Performance with YCSB on Lab
description: Procedure to benchmark HBase performance using YCSB on the lab environment with and without quotas applied, including setup, workload execution, and quota testing for read and write limits.
tags:
  - hbase
  - ycsb
  - benchmarking
  - quotas
  - read-quota
  - write-quota
  - lab
  - performance-testing
  - bigstreamer
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer Lab
  system: jakarta
  host_ip: 999.999.999.999
  tool: YCSB 0.17.0
  table_name: usertable
  namespaces:
    - default
    - quotas_test
  quotas:
    - read: 20req/sec
    - write: 20req/sec
  workloads: [workloada, workloadb, workloadc, workloadd, workloade, workloadf]
  hbase_config_path: /HBASE-HOME-DIR/conf
---
# Benchmarking HBASE on Lab with YCSB Tool
## Introduction
Our purpose was to run performance tests on a created Hbase table on Lab environment and document the results which will be used as a point of reference to evaluate the efficacy of quotas that will be applied. After running tests with no quotas, we run the same tests after setting firstly read throtttle quotas and secondly write quotas. We implemented the following procedure on jakarta node (999.999.999.999). Kinit with hbase keytab was a prerequisite.
## Create and Pre-Split HBase Table
This section creates the usertable using pre-splitting to distribute load evenly across regionservers.
- Created an hbase table using pre-splitting strategy to ensure write operations target region servers uniformly
```bash
hbase shell
n_splits = 300 # HBase recommends (10 * number of regionservers, in our case 3 regionservers)
create 'usertable', 'family', { SPLITS => (1..n_splits).map { |i| "user#{1000 + i * (9999 - 1000) / n_splits}" } }
```
## Install and Configure YCSB
This section describes downloading YCSB, extracting it, and pointing it to the HBase configuration directory.
- Get latest release of ycsb-0.17.0.tar.gz from https://github.com/brianfrankcooper/YCSB/releases/tag/0.17.0 on jakarta
- Unzip file
```bash
tar xfvz ycsb-0.17.0.tar.gz
```
- Specify a HBase config directory containing  hbase-site.xml
```bash
mkdir -p  /HBASE-HOME-DIR/conf
cd /HBASE-HOME-DIR/conf
cp /etc/hbase/conf/hbase-site.xml .
```
- Get to YCSB directory
```bash
cd ycsb-0.17.0
```
## Baseline HBase Performance Without Quotas
Run workloads A–F with YCSB against HBase before applying any read/write quotas to establish baseline metrics.
- Load the data
```bash
bin/ycsb load hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table=usertable -p columnfamily=family
```
- Execute the workload requesting a time series with 1 sec granularity and directing output to a datafile
```bash
bin/ycsb run hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table=usertable -p columnfamily=family -p measurementtype=timeseries -p timeseries.granularity=1000 -s > workloada.dat
```
- Delete and recreate table to repeat the aforementioned steps with workload{b-f} changing workload and datafiles respectively
```bash
hbase shell
disable 'usertable'
drop 'usertable'
exists 'usertable'
n_splits = 300
create 'usertable', 'family', { SPLITS => (1..n_splits).map { |i| "user#{1000 + i * (9999 - 1000) / n_splits}" } }
```
## Apply Read Quotas on HBase Namespace
Create a new HBase namespace and apply read throttle quotas to test impact on performance.
- Create namespace
```bash
hbase shell
create_namespace 'quotas_test'
list_namespace
```
- Create table in the namespace
```bash
hbase shell
n_splits = 300 # HBase recommends (10 * number of regionservers, in our case 3 regionservers)
create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}
```
- Set throttle quotas of type 'read'
```bash
hbase shell
set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => 'quotas_test', LIMIT => '20req/sec'
list_quotas
```
## Test Read Performance with Quotas Applied
- Load the data
```bash
bin/ycsb load hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family
```
- Execute the workload requesting a time series with 1 sec granularity and directing output to a datafile
```bash
bin/ycsb run hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family -p measurementtype=timeseries -p timeseries.granularity=1000 -s > workloada_read_quotas.dat
```
- Delete and recreate table to repeat the aforementioned steps with workload{b-f} changing workload and datafiles respectively
```bash
hbase shell
disable 'quotas_test:usertable'
drop 'quotas_test:usertable'
exists 'quotas_test:usertable'
n_splits = 300
create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}
```
## Switch from Read to Write Quotas
Remove read quotas and apply write quotas to the same namespace for comparative benchmarking.
- Remove read quotas
```bash
hbase shell
set_quota TYPE => THROTTLE, NAMESPACE => 'quotas_test', LIMIT => NONE
list_quotas
```
- Set write quotas
```bash
hbase shell
set_quota TYPE => THROTTLE, THROTTLE_TYPE => WRITE, NAMESPACE => 'quotas_test', LIMIT => '20req/sec'
list_quotas
```
-  Delete and recreate table to repeat to run tests with write quotas
```bash
hbase shell
disable 'quotas_test:usertable'
drop 'quotas_test:usertable'
exists 'quotas_test:usertable'
n_splits = 300
create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}
```
## Test Write Performance with Quotas Applied
- Load the data
```bash
bin/ycsb load hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family
```
- Execute the workload requesting a time series with 1 sec granularity and directing output to a datafile
```bash
bin/ycsb run hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family -p measurementtype=timeseries -p timeseries.granularity=1000 -s > workloada_write_quotas.dat
```
- Delete and recreate table to repeat the aforementioned steps with workload{b-f} changing workload and datafiles respectively
```bash
hbase shell
disable 'quotas_test:usertable'
drop 'quotas_test:usertable'
exists 'quotas_test:usertable'
n_splits = 300
create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}
```
**References:**
https://github.com/brianfrankcooper/YCSB#ycsb
https://github.com/brianfrankcooper/YCSB/tree/master/hbase2
https://github.com/brianfrankcooper/YCSB/wiki/Running-a-Workload
https://github.com/brianfrankcooper/YCSB/wiki/Core-Workloads
https://blog.cloudera.com/hbase-performance-testing-using-ycsb/