#check Retention
login @un2 as intra
1st level:
$ grep "Script Status" /shared/abc/cdo/log/203.Retention_Dynamic_Drop_DDL.202012.log | tail -n1

π.χ. Script Status ==> Scr:203.Retention_Dynamic_Drop_DDL.sh, Dt:2020-12-18 08:13:12, Status:0, Snapshot:1608267602, RunID:1608271202, ExpRows:3327, Secs:790, 00:13:10

if Status != 0 τοτε προβλημα

---

2nd level:
παιρνουμε απο το παραπανω το Snapshot ID (π.χ. Snapshot:1608267602)

$ egrep -i '(error|problem|excep|fail)' /shared/abc/cdo/log/Retention/*1608267602*.log

αν βγαλει < 10 δεν μας ανυσυχει ιδιαιτερα.
Αν βγαλει πολλα δεν ειναι καλό.

#Anonymization
$ grep "Script Status" /shared/abc/cdo/log/100.Anonymize_Data_Main.202012.log | tail -n1
p.x. Script Status ==> Scr:100.Anonymize_Data_Main.sh, Dt:2020-12-17 21:01:03, Status:, RunID:1608228002, Secs:3661, 01:01:01

παιρνουμε απο το παραπανω το RunID (π.χ. RunID:1608228002)
$ egrep '(:ERROR|with errors)' /shared/abc/cdo/log/Anonymize/*1608228002*.log | less

> 0 τοτε προβλημα