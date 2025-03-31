# Benchmarking HBASE on Lab with YCSB Tool

## Description
This document outlines the benchmarking procedure for HBase using the YCSB tool on the Lab environment. The objective is to establish a performance baseline before and after applying quotas.

## Prerequisites
- Access to `jakarta node (999.999.999.999)`.
- `hbase keytab` authentication.
- `YCSB Tool` downloaded from [YCSB GitHub](https://github.com/brianfrankcooper/YCSB/releases/tag/0.17.0).

## Procedure Steps

### **Step 1: HBase Table Creation**
- Create an HBase table using pre-splitting to distribute write operations:

    ```bash
    hbase shell
    n_splits = 300 # Recommended: 10 * number of regionservers (3 regionservers)
    create 'usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```

### **Step 2: Installing YCSB Tool and Configuring the System**
- Download and extract the YCSB tool:

    ```bash
    tar xfvz ycsb-0.17.0.tar.gz
    ```

- Specify an HBase configuration directory:

    ```bash
    mkdir -p /HBASE-HOME-DIR/conf
    cd /HBASE-HOME-DIR/conf
    cp /etc/hbase/conf/hbase-site.xml .
    ```

- Navigate to the YCSB directory:

    ```bash
    cd ycsb-0.17.0
    ```

### **Step 3: Performance Testing Without Quotas**
- Load test data:

    ```bash
    bin/ycsb load hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table=usertable -p columnfamily=family
    ```

- Run workload with 1-second granularity:

    ```bash
    bin/ycsb run hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table=usertable -p columnfamily=family -p measurementtype=timeseries -p timeseries.granularity=1000 -s > workloada.dat
    ```

- Reset the table and repeat tests for other workloads:

    ```bash
    hbase shell
    disable 'usertable'
    drop 'usertable'
    exists 'usertable'
    n_splits = 300
    create 'usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```

### **Step 4: Create Namespace and Apply Quotas**
- Create a namespace:

    ```bash
    hbase shell
    create_namespace 'quotas_test'
    list_namespace
    ```

- Create table within the namespace:

    ```bash
    hbase shell
    n_splits = 300
    create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```

- Apply **read quotas**:

    ```bash
    hbase shell
    set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => 'quotas_test', LIMIT => '20req/sec'
    list_quotas
    ```

### **Step 5: Performance Testing with Read Quotas**
- Load test data:

    ```bash
    bin/ycsb load hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family
    ```

- Run workload:

    ```bash
    bin/ycsb run hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family -p measurementtype=timeseries -p timeseries.granularity=1000 -s > workloada_read_quotas.dat
    ```

- Reset the table and repeat tests:

    ```bash
    hbase shell
    disable 'quotas_test:usertable'
    drop 'quotas_test:usertable'
    exists 'quotas_test:usertable'
    n_splits = 300
    create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```

### **Step 6: Remove Read Quotas and Apply Write Quotas**
- Remove **read quotas**:

    ```bash
    hbase shell
    set_quota TYPE => THROTTLE, NAMESPACE => 'quotas_test', LIMIT => NONE
    list_quotas
    ```

- Apply **write quotas**:

    ```bash
    hbase shell
    set_quota TYPE => THROTTLE, THROTTLE_TYPE => WRITE, NAMESPACE => 'quotas_test', LIMIT => '20req/sec'
    list_quotas
    ```

- Reset the table:

    ```bash
    hbase shell
    disable 'quotas_test:usertable'
    drop 'quotas_test:usertable'
    exists 'quotas_test:usertable'
    n_splits = 300
    create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```

### **Step 7: Performance Testing with Write Quotas**
- Load test data:

    ```bash
    bin/ycsb load hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family
    ```

- Run workload:

    ```bash
    bin/ycsb run hbase20 -P workloads/workloada -cp /HBASE-HOME-DIR/conf -p table='quotas_test:usertable' -p columnfamily=family -p measurementtype=timeseries -p timeseries.granularity=1000 -s > workloada_write_quotas.dat
    ```

- Reset the table and repeat tests:

    ```bash
    hbase shell
    disable 'quotas_test:usertable'
    drop 'quotas_test:usertable'
    exists 'quotas_test:usertable'
    n_splits = 300
    create 'quotas_test:usertable', 'family', {SPLITS => (1..n_splits).map {|i| "user#{1000+i*(9999-1000)/n_splits}"}}
    ```

## References

- [YCSB GitHub](https://github.com/brianfrankcooper/YCSB#ycsb)
- [HBase YCSB Module](https://github.com/brianfrankcooper/YCSB/tree/master/hbase2)
- [Running a YCSB Workload](https://github.com/brianfrankcooper/YCSB/wiki/Running-a-Workload)
- [YCSB Core Workloads](https://github.com/brianfrankcooper/YCSB/wiki/Core-Workloads)
- [HBase Performance Testing with YCSB](https://blog.cloudera.com/hbase-performance-testing-using-ycsb/)

