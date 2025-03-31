# OS Upgrade

## Description
This document outlines the procedure for upgrading the **OS packages** on **PR and DR edge nodes**, using the **mno Nexus Repository** as a yum proxy to the official Oracle repositories for **Oracle Linux 7.9**.

### **Affected Edge Nodes**
- `pr1edge01`
- `pr1edge02`
- `dr1edge01`
- `dr1edge02`

---

## Prerequisites
- **Administrator access** to edge nodes.
- **SSH access** to each node.
- **Nexus repository** correctly configured.
- **Cluster resource switchover** procedures should be followed before upgrading.

---

## Procedure Steps

### **1. Updating within the Same OS Version**
1. **SSH into the edge node**:
   ```bash
   ssh Exxxx@XXXedgeXX
   sudo -i
   ```

2. **Switchover cluster resources** (if required) before updating.
   > Follow the procedures described in the **Switchover of Cluster Resources** chapter  
   > **Security Vulnerabilities MOP**:  
   > [Click here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)

3. **Clean YUM cache and check available updates**:
   ```bash
   yum clean all
   yum check-update
   ```

4. **Proceed with the update**:
   ```bash
   yum update
   ```

5. **Reboot the system** to apply changes:
   ```bash
   systemctl reboot
   ```

6. **Verify OS version after reboot**:
   ```bash
   cat /etc/oracle-release
   ```

---

### **2. Rollback (Downgrade OS)**
If an issue occurs, you can **downgrade the OS packages**.

1. **SSH into the edge node**:
   ```bash
   ssh Exxxx@XXXedgeXX
   sudo -i
   ```

2. **Clean YUM cache**:
   ```bash
   yum clean all
   ```

3. **Downgrade OS packages**:
   ```bash
   yum downgrade
   ```

4. **Reboot the system**:
   ```bash
   reboot
   ```

5. **Verify OS version**:
   ```bash
   cat /etc/oracle-release
   ```

---

### **3. Configure Nexus Repositories**
Ensure that OS packages are **sourced from the Nexus repository** by setting up the correct repository configurations.

1. **SSH into the edge node**:
   ```bash
   ssh Exxxxx@XXXedgeXX
   sudo -i
   cd /etc/yum.repos.d
   ```

2. **Edit or create the following repository files**:

   - **el7_uek_latest.repo**
     ```bash
     vi el7_uek_latest.repo
     ```
     ```
     [el7_uek_latest]
     name = el7_uek_latest
     baseurl = http://999.999.999.999:8081/repository/el7_uek_latest/
     enabled = 1
     gpgcheck = 0
     exclude=postgresql*
     ```

   - **uek_release_4_packages.repo**
     ```bash
     vi uek_release_4_packages.repo
     ```
     ```
     [uek_release_4_packages]
     name = uek_release_4_packages
     baseurl = http://999.999.999.999:8081/repository/uek_release_4_packages/
     enabled = 1
     gpgcheck = 0
     exclude=postgresql*
     ```

   - **ol7_9_latest.repo**
     ```bash
     vi ol7_9_latest.repo
     ```
     ```
     [ol7_9_latest]
     name = ol7_9_latest
     baseurl = http://999.999.999.999:8081/repository/latest_packages/
     enabled = 1
     gpgcheck = 0
     exclude=postgresql*
     ```

   - **ol7_9_epel.repo**
     ```bash
     vi ol7_9_epel.repo
     ```
     ```
     [ol7_9_epel]
     name = ol7_9_epel
     baseurl = http://999.999.999.999:8081/repository/latest_epel_packages/
     enabled = 1
     gpgcheck = 0
     exclude=postgresql*
     ```

---

## Actions Taken / Expected Output
- OS is successfully **upgraded** to the latest Oracle Linux 7.9 version.
- **System reboots correctly** after the upgrade.
- The correct **Nexus repositories** are configured.
- OS version is **verified using `/etc/oracle-release`**.

### **Verification**
To confirm that the upgrade was successful:
```bash
cat /etc/oracle-release
```
> **Expected Output:** It should display the correct Oracle Linux 7.9 version.

---

## Notes and Warnings
> - **Always verify cluster resource switchover** before updating.
> - **Ensure that Nexus repositories** are properly set up before proceeding.
> - **Do not interrupt the upgrade process**, as it may cause system inconsistencies.

---

## Affected Systems / Scope
- **PR and DR Edge Nodes**
- **OS and Kernel Packages**
- **Cluster resources running on the updated nodes**

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Issue:** The OS upgrade fails with missing dependencies.  
  **Solution:** Ensure that the **Nexus repositories are properly configured**.

- **Issue:** The system fails to reboot after the upgrade.  
  **Solution:** Boot into **rescue mode** and check logs.

- **Issue:** `yum update` does not find updates.  
  **Solution:** Run:
  ```bash
  yum clean all
  yum check-update
  ```
  If the issue persists, verify the **repository URLs**.

### **Log File Locations**
```bash
tail -f /var/log/yum.log
tail -f /var/log/messages
```

---

## References
- [Security Vulnerabilities MOP](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)
- [Cloudera Documentation](https://www.cloudera.com/)

