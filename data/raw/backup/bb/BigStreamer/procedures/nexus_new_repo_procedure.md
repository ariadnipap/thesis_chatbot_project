# Add a New Repository on Nexus

## Description
This procedure describes how to add a new repository on **Nexus**, configure it, and ensure it is available for use on the system.

---

## Prerequisites
- Personal account access to an **edge node**.
- Access to **Nexus credentials**.
- SSH access to the node where the repository will be configured.
- Yum package manager installed on the system.

---

## Procedure Steps

### **1. Login to an Edge Node and Open Firefox**
1. SSH into an **edge node** with `-X` option to forward the display:
   ```bash
   ssh -X xedge0x
   ```
2. Open **Firefox**:
   ```bash
   firefox
   ```
3. When the **Firefox window** appears, navigate to:
   ```
   https://999.999.999.999:8081/
   ```
4. Log in with your **Nexus credentials**.
   > [Click here for the credentials](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/passwords.kdbx).

---

### **2. Create a New Repository**
1. Click on the **gear icon**.
2. Select **Repositories**.
3. Click on **Create Repository**.
4. Select **yum (proxy)** as the repository type.

---

### **3. Configure Repository Settings**
Enter the following values:
- **Name**: `name_of_repo`
- **Remote Storage URL**: `remdef_storage_url`
- **Maximum Component Age**: `20`
- **Minimum Component Age**: `20`
- **Clean Up Policies**: `daily_proxy_clean`

> **Leave all other settings as default.**

5. Click on **Create Repository** to save the new repository.

---

### **4. Configure the Repository on the System**
1. SSH into the node where the repository needs to be configured:
   ```bash
   ssh to_node
   ```
2. Edit the **Yum repository configuration file**:
   ```bash
   vi /etc/yum.repos.d/name_of_repo.repo
   ```
3. Add the following repository configuration:
   ```
   [name_of_repos]
   name = name_of_repo
   baseurl = http://999.999.999.999:8081/repository/name_of_repo.repo
   enabled = 1
   gpgcheck = 0
   ```

---

### **5. Verify and Enable the New Repository**
1. Clean the Yum cache:
   ```bash
   yum clean all
   ```
2. Check for repository updates:
   ```bash
   yum check-update > /tmp/test-repo.txt
   ```
3. List available repositories:
   ```bash
   yum repolist
   ```
> **Expected Output:** The new repository should be listed in the output.

---

## Actions Taken / Expected Output
- A new **Yum (proxy) repository** is successfully created in Nexus.
- The repository is configured on the target system.
- The repository appears in the `yum repolist` output.
- The system can successfully fetch updates from the new repository.

### **Verification**
To confirm that the repository is functioning correctly:
```bash
yum repolist | grep name_of_repo
```
> **Expected Output:** The repository name should appear in the list of available repositories.

---

## Notes and Warnings
> - **Ensure you have the correct Nexus credentials** before starting.
> - **Double-check repository names and URLs** to avoid misconfiguration.
> - If the repository does not appear in `yum repolist`, check the `baseurl` and ensure that Nexus is running.

---

## Affected Systems / Scope
- **Nexus Repository Manager**
- **Edge Nodes** where the repository is configured.
- **Any system relying on the new repository for package updates**.

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Issue:** Repository does not appear in `yum repolist`.  
  **Solution:** Verify the `baseurl` in `/etc/yum.repos.d/name_of_repo.repo`.

- **Issue:** `yum check-update` fails.  
  **Solution:** Ensure that Nexus is running and accessible at `http://999.999.999.999:8081/`.

- **Issue:** `firefox` does not open on the edge node.  
  **Solution:** Make sure SSH is started with `-X` and that the `DISPLAY` environment variable is set.

### **Log File Locations**
Check the Yum logs to debug repository issues:
```bash
tail -f /var/log/yum.log
```

---

## References
- [Cloudera Documentation](https://www.cloudera.com/)
- [Nexus Repository Manager](https://www.sonatype.com/products/nexus-repository)

