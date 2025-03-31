# Benchmarking HBASE on Lab with YCSB Tool

## Introduction

Our purpose was to run performance tests on a created Hbase table on Lab environment and document the results which will be used as a point of reference to evaluate the efficacy of quotas that will be applied. After running tests with no quotas, we run the same tests after setting firstly read throtttle quotas and secondly write quotas. We implemented the following procedure on jakarta node (999.999.999.999). Kinit with hbase keytab was a prerequisite.

## Hbase table creation

- Created an hbase table using pre-splitting strategy to ensure write operations target region servers uniformly
  
    ```bash
    hbase shell
    n_splits = 300 # HBase recommends (10 * number of regionservers, in our case 3 regionservers)
    create 'usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```

## Installing YCSB Tool and system configuration

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

## Performance tests on Hbase with YCSB before setting quotas

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
  create 'usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}
  ```
## Create namespace and set throttle quotas

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
    create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```
- Set throttle quotas of type 'read'
    ```bash
    hbase shell
    set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => 'quotas_test', LIMIT => '20req/sec'
    list_quotas
    ```
## Performance tests on Hbase with YCSB after setting quotas of type 'read'

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
## Remove read quotas and set write quotas

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
## Performance tests on Hbase with YCSB after setting quotas of type 'write'

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