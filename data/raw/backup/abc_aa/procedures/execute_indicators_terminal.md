### Execute Cube Indicators via Terminal

1. Connect to `un1.bigdata.abc.gr` and change user to `intra` using sudo.

2. Change directory 
```
cd projects/cube_ind
```

3. Remove old pyspark script
```
rm Indicators_Spark_Job.py
```

4. Get new one from HDFS
```
kinit -kt /home/intra/intra.keytab intra
hdfs dfs -get /user/intra/cube/Indicators_Spark_Job.py
```

6. Edit submit script to change execution date. Execution date equals the missing date + 2. E.g data for 20210101 will be loaded on 20210103.
```
vim run_cube.sh
...verhead=4096 Indicators_Spark_Job.py <date> brond.dsl_s...
```

7. Run the submit script 
```
./run_cube.sh
```
