---
title: "abc - Retention and Anonymization Job Status Checks"
description: "Instructions for checking the status and logs of Retention_Dynamic_Drop_DDL and Anonymize_Data_Main shell scripts on abc using Snapshot ID and RunID from log files."
tags:
  - abc
  - BigStreamer
  - retention
  - anonymization
  - job monitoring
  - script status
  - log analysis
  - shell commands
  - troubleshooting
  - snapshot
  - runid
---
## Retention Check
### Step 1 – Initial Status Check
Login to `un2` as `intra` and run the following command:
```bash
grep "Script Status" /shared/abc/cdo/log/203.Retention_Dynamic_Drop_DDL.202012.log | tail -n1
```
Example output:
Script Status ==> Scr:203.Retention_Dynamic_Drop_DDL.sh, Dt:2020-12-18 08:13:12, Status:0, Snapshot:1608267602, RunID:1608271202, ExpRows:3327, Secs:790, 00:13:10
If Status != 0, the script has failed.
---
### Step 2 – Deeper Investigation
Extract the Snapshot value from the above output (e.g. 1608267602) and check for any logged problems:
```bash
egrep -i '(error|problem|except|fail)' /shared/abc/cdo/log/Retention/*1608267602*.log
```
If the result has fewer than 10 lines, it’s usually not concerning. A large number of matches indicates an issue.
## Anonymization Check
### Step 1 – Initial Status Check
``` bash
grep "Script Status" /shared/abc/cdo/log/100.Anonymize_Data_Main.202012.log | tail -n1
```
Example output:
Script Status ==> Scr:100.Anonymize_Data_Main.sh, Dt:2020-12-17 21:01:03, Status:, RunID:1608228002, Secs:3661, 01:01:01
### Step 2 – Check Detailed Errors
Extract the RunID (e.g. 1608228002) and inspect logs:
```bash
egrep '(:ERROR|with errors)' /shared/abc/cdo/log/Anonymize/*1608228002*.log | less
```
If the command returns output, there is a problem.
## Notes
- All paths refer to shared log directories on abc BigStreamer.
- Retention jobs refer to dropping old data.
- Anonymization jobs refer to data privacy transformations.
---