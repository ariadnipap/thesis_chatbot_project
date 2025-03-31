# Fix MySQL Replication

## Description
This procedure details how to **repair MySQL replication** when it stops due to **invalid queries** or other issues. The process includes **identifying the issue, restoring from a backup, and restarting replication**.

### **Affected MySQL Instances**
#### PR
- **Master MySQL Host**: `pr1node03.mno.gr`
- **Slave MySQL Host**: `pr1node02.mno.gr`
- **Port**: `3306`
- **Configuration File**: `/etc/my.cnf`
- **Data Path**: `/var/lib/mysql/`
- **General Log File**: `/var/log/mysqld.log`
- **Error Log File**: `/var/log/mysqld_error.log`
- **User**: `mysql`
- **Password**: [prodsyspasswd.kbdx](/KnowledgeBase/prodsyspasswd.kdbx)

#### DR
- **Master MySQL Host**: `dr1node03.mno.gr`
- **Slave MySQL Host**: `dr1node02.mno.gr`
- **Port**: `3306`
- **Configuration File**: `/etc/my.cnf`
- **Data Path**: `/var/lib/mysql/`
- **General Log File**: `/var/log/mysqld.log`
- **Error Log File**: `/var/log/mysqld_error.log`
- **User**: `mysql`
- **Password**: [prodsyspasswd.kbdx](/KnowledgeBase/prodsyspasswd.kdbx)

---

## Prerequisites
- **Administrator access** to MySQL slave servers.
- **SSH access** to slave and master MySQL servers.
- **A recent MySQL dump backup** for restoration.
- **Check the replication status** before applying fixes.

---

## Procedure Steps

### **1. Identify the Problem**
1. **SSH into the MySQL slave node**:
   ```bash
   ssh root@pr1node02.mno.gr
   ```

2. **Check MySQL replication status**:
   ```bash
   mysql -u root -p
   SHOW SLAVE STATUS\G;
   ```

3. **Identify issues**:
   - If either **`Slave_IO_Running`** or **`Slave_SQL_Running`** is set to `No`, the replication is broken.

---

### **2. Stop the MySQL Slave Process**
1. **Stop the slave process**:
   ```bash
   mysql -u root -p
   STOP SLAVE;
   ```

2. **Verify that both `Slave_IO_Running` & `Slave_SQL_Running` are set to `No`**:
   ```bash
   SHOW SLAVE STATUS\G;
   ```

---

### **3. Restore from MySQL Backup**
1. **Navigate to the backup directory**:
   ```bash
   cd /backup
   ls -ltr
   ```

2. **Find the latest MySQL backup file**:
   ```bash
   tar -ztvf /backup/DRBDA_year-month-day.tar.gz | grep -i mysql_backup
   ```
   > This command lists backup files stored in tar.gz format.

3. **Extract the MySQL backup file**:
   ```bash
   tar -zxvf /backup/DRBDA_year-month-day.tar.gz mysql_backup_yearmonthday.sql.gz
   ```

4. **Decompress the extracted MySQL dump**:
   ```bash
   gunzip mysql_backup_yearmonthday.sql.gz
   ```

5. **Restore the MySQL database from backup**:
   ```bash
   mysql -uroot -p < mysql_backup_yearmonthday.sql
   ```

---

### **4. Restart MySQL Replication**
1. **Verify the restoration was successful**:
   ```bash
   mysql -u root -p
   SHOW SLAVE STATUS\G;
   ```
   - No errors should be displayed in `Last_Error`.

2. **Start the MySQL slave process**:
   ```bash
   START SLAVE;
   ```

3. **Check if replication is working again**:
   ```bash
   SHOW SLAVE STATUS\G;
   ```
   - **Both `Slave_IO_Running` and `Slave_SQL_Running` should be set to `Yes`.**
   - **`Seconds_Behind_Master` should be `0` after some minutes.**

---

## Actions Taken / Expected Output
- **Replication is stopped, backup is restored, and replication is restarted**.
- **No errors should exist in `Last_Error`**.
- **`SHOW SLAVE STATUS\G;` should display both `Slave_IO_Running` and `Slave_SQL_Running` as `Yes`**.
- **Replication should be caught up with the master (`Seconds_Behind_Master = 0`).**

### **Verification**
Run:
```bash
SHOW SLAVE STATUS\G;
```
> **Expected Output:**
> - `Slave_IO_Running: Yes`
> - `Slave_SQL_Running: Yes`
> - `Seconds_Behind_Master: 0`

---

## Notes and Warnings
> - **Only apply this procedure if replication has stopped.**
> - **Verify the backup before restoring**, to avoid data loss.
> - **MySQL logs should be checked for errors before and after the process.**
> - If replication does not resume, **check the MySQL error logs**.

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Issue:** Replication does not start even after running `START SLAVE`.  
  **Solution:** Check the MySQL error logs:
  ```bash
  tail -f /var/log/mysqld_error.log
  ```

- **Issue:** `Seconds_Behind_Master` is continuously increasing.  
  **Solution:** Check for slow queries:
  ```bash
  SHOW PROCESSLIST;
  ```

- **Issue:** `Last_Error` displays a duplicate key error.  
  **Solution:** Skip the problematic transaction:
  ```bash
  SET GLOBAL SQL_SLAVE_SKIP_COUNTER = 1;
  START SLAVE;
  ```

### **Log File Locations**
```bash
tail -f /var/log/mysqld.log
tail -f /var/log/mysqld_error.log
```

---

## Affected Systems / Scope
- **PR and DR MySQL slave servers**
- **Replication-dependent applications**
- **Any system relying on up-to-date MySQL data**

---

## References
- [MySQL Replication Documentation](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
- [Cloudera MySQL Guide](https://www.cloudera.com/)
- [Security Vulnerabilities MOP](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)

