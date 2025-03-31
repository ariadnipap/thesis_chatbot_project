# abc - BigStreamer - How to open a ticket to DELL


<b>Description:</b>

```
Παρακάτω περιγράφεται βήμα βήμα η διαδικασία ανοίγματος ενός ticket έως και την συλλογή των TSR logs από την IDRAC.
```

<b>Actions Taken:</b>

1. ssh with your personal account on the issue node.
2. sudo -i;ipmitool lan print | grep -i 'IP Address' # To find the Managment IP. Otherwise e.g grep nodew /etc/hosts 
```
If the ipmitool package did not exist just install it. yum install ipmitool;
```
3. connect via vnc. Open firefox and type the `IP Address` from step 2
4. From `Server-->Overview-->Server Information` copy the `Service Tag number`
5. Call Dell support `2108129800`. They need the `Service Tag number` from step 4
6. An engineer will create a case and sent you all the necessary steps. If not the link to collect the TSR logs is `https://www.dell.com/support/kbdoc/el-gr/000126803/export-a-supportassist-collection-via-idrac7-and-idrac8`
7. Inform `abc` before any action on the IDRAC.
8. Download localy the TSR gz file. ssh on the node with vnc (e.g un4). The downloaded files stored under `/home/cloudera/Downloads/` and the format is `TSRdate_service_tag.zip`
9. Send the zip file/files to DELL and wait for their response.

Done!
