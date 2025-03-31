# Check Retention

## Description
This procedure outlines the steps to check retention logs and identify potential issues.

## Prerequisites
- SSH access to `un2` as `intra`.
- Permissions to access log files in `/shared/abc/cdo/log/`.

## Procedure Steps

### 1. First Level Check
- Log in to `un2` as `intra`.
- Run the following command to check the script status:
  ```bash
  grep "Script Status" /shared/abc/cdo/log/203.Retention_Dynamic_Drop_DDL.202012.log | tail -n1
  ```
- Example output:
  ```
  Script Status ==> Scr:203.Retention_Dynamic_Drop_DDL.sh, Dt:2020-12-18 08:13:12, Status:0, Snapshot:1608267602, RunID:1608271202, ExpRows:3327, Secs:790, 00:13:10
  ```
- If `Status != 0`, then there is a problem.

### 2. Second Level Check
- Extract the `Snapshot ID` from the previous command output (e.g., `Snapshot:1608267602`).
- Run the following command to check for errors:
  ```bash
  egrep -i '(error|problem|excep|fail)' /shared/abc/cdo/log/Retention/*1608267602*.log
  ```
- If the output contains **less than 10 errors**, it is not a major concern.  
- If there are **many errors**, it indicates a problem.

---

## Anonymization Check

### 1. First Level Check
- Run the following command to check the anonymization script status:
  ```bash
  grep "Script Status" /shared/abc/cdo/log/100.Anonymize_Data_Main.202012.log | tail -n1
  ```
- Example output:
  ```
  Script Status ==> Scr:100.Anonymize_Data_Main.sh, Dt:2020-12-17 21:01:03, Status:, RunID:1608228002, Secs:3661, 01:01:01
  ```

### 2. Second Level Check
- Extract the `RunID` from the previous command output (e.g., `RunID:1608228002`).
- Run the following command to check for errors:
  ```bash
  egrep '(:ERROR|with errors)' /shared/abc/cdo/log/Anonymize/*1608228002*.log | less
  ```
- If the output is **greater than 0**, then there is a problem.

## Actions Taken / Expected Output
- If `Status` is `0`, there is no issue.
- If errors are detected in the logs, further investigation is needed.

## Notes and Warnings
> A low number of error messages in logs is not a major concern, but a large number indicates an issue.

## Affected Systems / Scope
- Log retention system
- Data anonymization process

## Troubleshooting / Error Handling
- If errors are found, analyze the relevant logs to determine the root cause.
- If retention scripts fail, check permissions and configurations.

## References

