#check Retention
login @un2 as intra
1st level:
$ grep "Script Status" /shared/abc/cdo/log/203.Retention_Dynamic_Drop_DDL.202012.log | tail -n1

π.χ. Script Status ==> Scr:203.Retention_Dynamic_Drop_DDL.sh, Dt:2020-12-18 08:13:12, Status:0, Snapshot:1608267602, RunID:1608271202, ExpRows:3327, Secs:790, 00:13:10

if Status != 0 we have a problem

---

2nd level:
we get the Snapshot ID from the above (e.g. Snapshot:1608267602)

$ egrep -i '(error|problem|except|fail)' /shared/abc/cdo/log/Retention/*1608267602*.log

if it comes out < 10 it doesn't particularly worry us.
If it comes out a lot it's not good.

#Anonymization
$ grep "Script Status" /shared/abc/cdo/log/100.Anonymize_Data_Main.202012.log | tail -n1
ex: Script Status ==> Scr:100.Anonymize_Data_Main.sh, Dt:2020-12-17 21:01:03, Status:, RunID:1608228002, Secs:3661, 01:01:01

we take RunID from the above (π.χ. RunID:1608228002)
$ egrep '(:ERROR|with errors)' /shared/abc/cdo/log/Anonymize/*1608228002*.log | less

> 0 we have a problem
