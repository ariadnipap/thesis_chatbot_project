# PostgreSQL Upgrade

## Description
This procedure details the steps required to upgrade PostgreSQL from **9.5 to 14** on **PR and DR edge nodes**, including **repository setup, installation, data migration, and rollback procedures**.

### **Affected Edge Nodes**
- `pr1edge01`
- `pr1edge02`
- `dr1edge01`
- `dr1edge02`

---

## Prerequisites
- **Administrator access** to edge nodes.
- **SSH access** to each node.
- **Cluster resource switchover procedures** should be followed before upgrading.
- **Backup of PostgreSQL data and configuration files**.

---

## Procedure Steps

### **1. Preparation**
1. **SSH into the edge node**:
   ```bash
   ssh Exxxx@XXXedgeXX
   sudo -i
   ```

2. **Switchover cluster resources** (if required) before upgrading.
   > Follow the procedures described in the **Switchover of Cluster Resources** chapter  
   > **Security Vulnerabilities MOP**:  
   > [Click here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)

3. **Stop PostgreSQL 9.5 Service**:
   ```bash
   sudo -iu postgres
   systemctl stop postgresql-9.5.service
   systemctl disable postgresql-9.5.service
   systemctl status postgresql-9.5.service
   ```

4. **Backup PostgreSQL data** on each edge server:
   ```bash
   pg_dumpall > edgeXX_postgres_backup
   ```

5. **Backup PostgreSQL Configuration Files**:
   ```bash
   cp -ap /var/lib/psql/9.5/data/pg_hba.conf /var/lib/psql/9.5/data/pg_hba.conf.bak
   cp -ap /var/lib/psql/9.5/data/postgresql.conf /var/lib/psql/9.5/data/postgresql.conf.bak
   ```

---

### **2. Create PostgreSQL 14 Repositories**
1. **Download RPMs** for PostgreSQL 14 from:  
   [PostgreSQL Repository](https://download.postgresql.org/pub/repos/yum/14/redhat/rhel-7.9-x86_64/)

2. **SSH into `pr1node01`** and create the repository:
   ```bash
   ssh Exxxx@pr1node01
   sudo -i
   mkdir -p /var/www/postgres14/Packages/
   ```

3. **Move RPM files into the repository**:
   ```bash
   mv postgresql14*.rpm /var/www/html/postgres14/Packages/
   ```

4. **Create or update the repository**:
   ```bash
   cd /var/www/postgres14/
   createrepo .
   # If repository already exists:
   createrepo --update .
   ```

5. **Create and distribute the repository file**:
   ```bash
   ssh Exxx@pr1edge01
   sudo -i
   vi /etc/yum.repos.d/postgres14.repo
   ```
   Add the following:
   ```
   [postgres14]
   name = Postgres14
   baseurl = http://pr1node01.mno.gr/postgres14/
   enabled = 1
   gpgcheck = 0
   ```

6. **Copy the repository file to all edge nodes**:
   ```bash
   scp /etc/yum.repos.d/postgres14.repo XXXedgeXX:/etc/yum.repos.d/
   ```

7. **Disable the old PostgreSQL repository**:
   - Edit the old repo file under `/etc/yum.repos.d/`
   - Set `enabled = 0`

---

### **3. Upgrade PostgreSQL**
1. **SSH into the edge node**:
   ```bash
   ssh Exxxx@XXXedgeXX
   sudo -i
   ```

2. **Clean YUM cache and install PostgreSQL 14**:
   ```bash
   yum clean all
   yum install --disablerepo=* --enablerepo=postgres14 postgresql14 postgresql14-server postgresql14-contrib postgresql14-libs
   ```

3. **Change PostgreSQL Data Directory**:
   ```bash
   vi /usr/lib/systemd/system/postgresql-14.service
   ```
   Update the **PGDATA** environment variable:
   ```
   Environment=PGDATA=/var/lib/pgsql/9.14/data
   ```

4. **Initialize PostgreSQL 14 and enable the service**:
   ```bash
   /usr/pgsql-14/bin/postgresql-14-setup initdb
   systemctl enable --now postgresql-14
   ```

---

### **4. Restore Data from Backup**
1. **SSH into each edge node**:
   ```bash
   ssh Exxx@XXXedgeXX
   sudo -iu postgres
   ```

2. **Restore the database backup**:
   ```bash
   psql -f edgeXX_postgres_backup postgres
   ```

3. **Restart and verify the PostgreSQL 14 service**:
   ```bash
   systemctl restart postgresql-14.service
   systemctl status postgresql-14.service
   ```

4. **Compare Configuration Files for Differences**:
   ```bash
   sdiff /var/lib/pgsql/9.14/data/pg_hba.conf /var/lib/psql/9.5/data/pg_hba.conf
   sdiff /var/lib/pgsql/9.14/data/postgresql.conf /var/lib/psql/9.5/data/postgresql.conf
   ```

5. **If everything is OK, unstandby the node**.

---

### **5. Rollback (Downgrade to PostgreSQL 9.5)**
1. **SSH into the edge node**:
   ```bash
   ssh Exxx@XXXedgeXX
   sudo -iu postgres
   ```

2. **Stop and disable PostgreSQL 14**:
   ```bash
   systemctl disable --now postgresql-14.service
   systemctl status postgresql-14.service
   ```

3. **Downgrade PostgreSQL using YUM**:
   ```bash
   sudo -i
   yum clean all
   yum downgrade --disablerepo=* --enablerepo=postgres9 postgresql
   ```

4. **Enable and start PostgreSQL 9.5**:
   ```bash
   systemctl enable --now postgresql-9-5.service
   ```

---

## Actions Taken / Expected Output
- **PostgreSQL is successfully upgraded** from version **9.5 to 14**.
- **Data is backed up and restored** correctly.
- **New PostgreSQL repositories are configured** and old ones are disabled.
- **PostgreSQL 14 is running and verified**.

### **Verification**
Check PostgreSQL version:
```bash
psql -c "SELECT version();"
```
> **Expected Output:** PostgreSQL 14.x should be displayed.

---

## Notes and Warnings
> - **Ensure backups are taken** before proceeding.
> - **Do not interrupt the upgrade process**, as it may cause data corruption.
> - **Always verify cluster resource switchover** before upgrading.
> - **Configuration files may need manual adjustment** after upgrade.

---

## Affected Systems / Scope
- **PR and DR Edge Nodes**
- **PostgreSQL Databases**
- **Application Services relying on PostgreSQL**

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Issue:** PostgreSQL 14 does not start.  
  **Solution:** Check logs for errors:
  ```bash
  journalctl -u postgresql-14 --no-pager
  ```

- **Issue:** Data restore fails.  
  **Solution:** Ensure that the backup file is not corrupted.

- **Issue:** Configuration settings differ between versions.  
  **Solution:** Manually review and adjust `/var/lib/pgsql/9.14/data/postgresql.conf`.

### **Log File Locations**
```bash
tail -f /var/log/postgresql/postgresql-14.log
```

---

## References
- [PostgreSQL Official Repository](https://download.postgresql.org/pub/repos/yum/)
- [Security Vulnerabilities MOP](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)

