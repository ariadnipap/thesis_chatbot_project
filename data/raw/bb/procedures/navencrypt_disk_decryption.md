# Below procedure describes how to decrypt an encrypted disk


###### Back up 
Backup data of encrypted disk

>Ndef_1: In our case we don't have data in this partition. So, we don't have to backup

```bash
tar zcvf /backup/data_1-$(date +%Y-%m-%d).tar.gz /data/1
```

###### Decrypt encrypted disk

1. Make sure that Kafka and Kudu services are down

>Ndef_2: You should stop kafka and kudu in case we have data at `/data/1` partition. In our case we don't have data so we skip this step

- From Cloudera Manager > Kafka > Stop

- From Cloudera Manager > Kudu > Stop

2. Check that KTS is up and running

From Cloudera Manager with admin account:

- Go to Keytrustee > Key Trustee Server  

3. Remove /data/1 mountpoint that is no longer in use
```bash
navencrypt-prepare --undo-force /data/1
```
4. Check ztab:
```bash
cat /etc/navencrypt/ztab | grep /data/1
```
The output should be commented 

5. List the mountpoints
```bash
mount -l
```

6. Uncomment the decrypted mount points on fstab

Uncomment line for `/dev/mapper/ol_pr1edge01-data_1 /data/1 xfs defauts 0 0` at `/etc/fstab`

7. Check if disk is mounted with below command
```bash
mount -a
```

8. Move data from backup directory back to decrypted disk

>Ndef_3: Occurs only if step 1 is performed
```bash
tar -xvf /backup/data_1.tar.gz -C /data/1
```


9. Start kudu and kafka

>Ndef_4: Occurs only if step 1 is performed 

- From Cloudera Manager > Kafka > Start

- From Cloudera Manager > Kudu > Start
