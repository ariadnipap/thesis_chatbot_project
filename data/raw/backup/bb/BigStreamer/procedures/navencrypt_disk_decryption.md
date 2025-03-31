# Decrypt an Encrypted Disk

## Description
This procedure outlines the steps required to decrypt an encrypted disk, including stopping relevant services, removing encryption settings, and restoring data if necessary.

## Prerequisites
- Administrative access to the system.
- Cloudera Manager access to manage Kafka and Kudu services.
- Backup of any existing data on the encrypted disk (if applicable).
- Access to **Key Trustee Server (KTS)** via Cloudera Manager.

---

## Procedure Steps

### 1. Back Up Data (If Applicable)
Before decrypting the disk, back up any existing data.
```bash
tar zcvf /backup/data_1-$(date +%Y-%m-%d).tar.gz /data/1
```
> **Ndef_1:** In this case, there is no data on the partition, so this step can be skipped.

---

### 2. Stop Kafka and Kudu Services (If Applicable)
Before proceeding, stop Kafka and Kudu to avoid data corruption.

- From **Cloudera Manager**:
  - **Kafka** → **Stop**
  - **Kudu** → **Stop**

> **Ndef_2:** This step is only required if `/data/1` contains data. Since the partition is empty in this case, this step can be skipped.

---

### 3. Verify Key Trustee Server (KTS) is Running
1. Log in to Cloudera Manager with an **admin account**.
2. Navigate to:
   ```
   Cloudera Manager > Keytrustee > Key Trustee Server
   ```
3. Ensure **Key Trustee Server (KTS)** is up and running.

---

### 4. Remove `/data/1` Mountpoint
Remove the encryption settings for the mountpoint.
```bash
navencrypt-prepare --undo-force /data/1
```

---

### 5. Verify `/etc/navencrypt/ztab` Configuration
Check that `/data/1` is commented out.
```bash
cat /etc/navencrypt/ztab | grep /data/1
```
> **Expected Output:** The entry should be commented.

---

### 6. List Current Mountpoints
```bash
mount -l
```
Verify that `/data/1` is no longer listed as an encrypted mountpoint.

---

### 7. Uncomment Decrypted Mountpoint in `/etc/fstab`
Edit `/etc/fstab` and uncomment the following line:
```
/dev/mapper/ol_pr1edge01-data_1 /data/1 xfs defaults 0 0
```

---

### 8. Mount the Disk
Ensure the disk is mounted.
```bash
mount -a
```
> **Expected Output:** The disk should be successfully mounted as `/data/1`.

---

### 9. Restore Data from Backup (If Applicable)
If step 1 was performed, restore the data back to the decrypted disk.
```bash
tar -xvf /backup/data_1.tar.gz -C /data/1
```
> **Ndef_3:** This step is only required if data was backed up earlier.

---

### 10. Start Kafka and Kudu Services (If Applicable)
If step 2 was performed, restart Kafka and Kudu.

- From **Cloudera Manager**:
  - **Kafka** → **Start**
  - **Kudu** → **Start**

> **Ndef_4:** This step is only required if the services were stopped earlier.

---

## Actions Taken / Expected Output
- The encrypted disk is successfully **decrypted**.
- **Key Trustee Server (KTS)** is verified as **running**.
- **Kafka and Kudu services** are restarted (if they were stopped).
- Data is restored (if backup was performed).
- `/data/1` is successfully **mounted** and accessible.

### **Verification**
To confirm that the disk is decrypted and mounted correctly:
```bash
df -h | grep /data/1
```
> **Expected Output:** `/data/1` should appear as a mounted partition.

---

## Notes and Warnings
> - **Ensure backups are taken before proceeding** if the partition contains data.
> - **Stopping Kafka and Kudu is only necessary** if `/data/1` has data.
> - If decryption fails, **verify that KTS is running** and that `/etc/fstab` is correctly updated.

---

## Affected Systems / Scope
- **Kafka** and **Kudu** services (if data exists on `/data/1`).
- **Encrypted disk partition (`/data/1`)**.

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Issue:** `/data/1` does not mount after running `mount -a`.  
  **Solution:** Check `/etc/fstab` for incorrect entries and verify that the disk exists.

- **Issue:** Kafka and Kudu fail to start after decryption.  
  **Solution:** Check logs for errors:
  ```bash
  tail -f /var/log/kafka/*.log
  tail -f /var/log/kudu/*.log
  ```

- **Issue:** Decryption fails with `navencrypt-prepare` error.  
  **Solution:** Ensure that **Key Trustee Server (KTS) is running** in Cloudera Manager.

---

## References
- [Cloudera Manager Documentation](https://www.cloudera.com/)

