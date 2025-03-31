# Enable ACLs in Spark and YARN

## Description
This procedure details the steps required to **enable ACLs in YARN and Spark** to grant specific groups access to Spark logs. The steps include **modifying YARN configuration and enabling Spark ACL settings**.

---

## Prerequisites
- **Administrator access** to Cloudera Manager.
- **SSH access** to YARN and Spark cluster nodes.
- **Knowledge of required user groups** that need access.

---

## Procedure Steps

### **1. YARN Configuration**
1. **Navigate to YARN ACL settings**:
   - Open **Cloudera Manager**.
   - Go to **YARN → Configuration**.
   - Search for **"ACL For Viewing A Job"**.

2. **Modify the ACL settings**:
   - Add the required groups to **view MapReduce jobs**.
   - Example configuration:
     ```
     hue WBDADMIN,WBDOPDEV,WBDOPPRO,WBDOPQA
     ```
   - **Ensure correct syntax** by clicking the question mark (?) next to the setting.

3. **Enable Job ACL JobHistory Server Default Group**:
   - Locate **"Enable Job ACL JobHistory Server Default Group"**.
   - Set it to **enabled**.

---

### **2. Spark Configuration**
1. **Navigate to Spark ACL settings**:
   - Open **Cloudera Manager**.
   - Go to **Spark → Configuration**.
   - Search for **"Spark Client Advanced Configuration Snippet"**.

2. **Modify the Spark ACL settings**:
   - Enable Spark ACLs:
     ```bash
     spark.acls.enable=true
     ```
   - Enable ACLs for admin groups:
     ```bash
     spark.admin.acls.groups=WBDADMIN
     ```
   - Allow Spark History Server access to a group:
     ```bash
     spark.history.ui.admin.acls.groups=WBDADMIN
     ```
   - Set groups allowed to view Spark UI:
     ```bash
     spark.ui.view.acls.groups=WBDOPDEV,WBDOPPRO,WBDOPQA
     ```

---

## Actions Taken / Expected Output
- **YARN and Spark ACL settings are updated** to grant access to specified groups.
- **YARN Job ACLs allow specified users to view MapReduce jobs**.
- **Spark ACLs control log access for admin and UI viewers**.

### **Verification**
- **Check YARN ACLs**:
  ```bash
  yarn application -list -appStates RUNNING
  ```
  - Expected output: **Users in the specified groups can view running jobs**.

- **Check Spark ACL settings**:
  ```bash
  spark-shell --conf spark.ui.view.acls.groups=WBDOPDEV,WBDOPPRO,WBDOPQA
  ```
  - Expected output: **Spark UI should allow access to specified groups**.

---

## Notes and Warnings
> - **Ensure correct syntax when modifying ACLs**, as incorrect syntax can cause access issues.
> - **Apply changes during a maintenance window** to avoid disruptions.
> - **Restart Spark and YARN services after making changes** for them to take effect.

---

## Affected Systems / Scope
- **YARN Resource Manager and Job History Server**
- **Spark Cluster and Spark History Server**
- **Users accessing Spark logs and UIs**

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Issue:** Users cannot access Spark logs despite being in the ACL group.  
  **Solution:** Restart Spark services:
  ```bash
  systemctl restart spark-history-server
  ```

- **Issue:** YARN ACL settings do not take effect.  
  **Solution:** Restart YARN services:
  ```bash
  systemctl restart hadoop-yarn-resourcemanager
  ```

- **Issue:** Spark UI does not reflect ACL changes.  
  **Solution:** Clear Spark history server cache:
  ```bash
  rm -rf /tmp/spark-events/*
  systemctl restart spark-history-server
  ```

### **Log File Locations**
```bash
tail -f /var/log/spark/spark-history-server.log
tail -f /var/log/hadoop-yarn/yarn-resourcemanager.log
```

---

## References
- [Apache Spark ACL Documentation](https://spark.apache.org/docs/latest/security.html)
- [Apache YARN ACL Documentation](https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/ResourceManagerAccessControl.html)

