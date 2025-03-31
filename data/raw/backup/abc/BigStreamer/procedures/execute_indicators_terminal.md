# Execute Cube Indicators via Terminal

## Description
This procedure outlines the steps to execute the Cube Indicators process via terminal by updating the necessary scripts and running the job.

## Prerequisites
- SSH access to `un1.bigdata.abc.gr`.
- Permissions to switch to the `intra` user.
- Access to HDFS to retrieve the latest PySpark script.

## Procedure Steps

### 1. Connect to `un1.bigdata.abc.gr`
- SSH into the server and switch to the `intra` user:
  ```bash
  ssh un1.bigdata.abc.gr
  sudo -i -u intra
  ```

### 2. Navigate to the Project Directory
- Change to the `cube_ind` directory:
  ```bash
  cd projects/cube_ind
  ```

### 3. Remove the Old PySpark Script
- Delete the outdated script:
  ```bash
  rm Indicators_Spark_Job.py
  ```

### 4. Retrieve the New PySpark Script from HDFS
- Authenticate with Kerberos and download the updated script:
  ```bash
  kinit -kt /home/intra/intra.keytab intra
  hdfs dfs -get /user/intra/cube/Indicators_Spark_Job.py
  ```

### 5. Edit the Submit Script to Update Execution Date
- Open `run_cube.sh` and modify the execution date.
- The execution date should be the missing date +2 days.
- Example: Data for `20210101` will be loaded on `20210103`.
  ```bash
  vim run_cube.sh
  ```
- Example edit within the script:
  ```
  ...verhead=4096 Indicators_Spark_Job.py <date> brond.dsl_s...
  ```

### 6. Run the Submit Script
- Execute the script to start the job:
  ```bash
  ./run_cube.sh
  ```

## Actions Taken / Expected Output
- The latest `Indicators_Spark_Job.py` script is retrieved and used for execution.
- The `run_cube.sh` script is updated with the correct execution date.
- The job executes successfully, processing Cube Indicators data.

## Notes and Warnings
> Ensure that the execution date is set correctly before running the job.  
> Always fetch the latest script from HDFS to avoid outdated data processing.

## Affected Systems / Scope
- Cube Indicators pipeline
- `brond.dsl_s` data processing

## Troubleshooting / Error Handling
- If the script fails to retrieve data, check HDFS permissions:
  ```bash
  hdfs dfs -ls /user/intra/cube/
  ```
- If execution fails, inspect logs:
  ```bash
  tail -f run_cube.log
  ```
- Verify Kerberos authentication:
  ```bash
  klist
  ```

## References
