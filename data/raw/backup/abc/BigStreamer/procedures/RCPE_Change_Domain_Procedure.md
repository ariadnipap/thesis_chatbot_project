# RCPE Integration with GROUPNET

## Description
This procedure describes the steps required to change the current domain from `central-domain.root.def.gr` to `groupnet` along with user migration and system updates.

## Prerequisites
- Verify SSL certificates for `groupnet` have been imported.
- An active user from the new domain must be provided for testing.
- `/etc/hosts` file must be updated on all BigStreamer servers with the new domain.
- Perform an LDAP search to validate user existence:
  ```bash
  ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -W -b "dc=groupnet,dc=gr" -D "<Bind User sAMAccountName>" '(sAMAccountName=...)'
  ```

## Affected Systems / Scope
- **Production Servers:**
  - `rcpe1.bigdata.abc.gr`
  - `rcpe2.bigdata.abc.gr`
- **Test Servers:**
  - `unc2.bigdata.abc.gr`
- **Application URLs:**
  - Production:
    - `https://999.999.999.999:8843/rcpe/#/login`
    - `https://cne.def.gr:8843/rcpe/#/login`
  - Test:
    - `https://999.999.999.999:8743/rcpe/`

> **Note:** The following steps apply to the test environment. Ensure the same steps are applied in production.

---

## Procedure Steps

### **1. Create a New Domain in RCPE**
1. Login to `https://999.999.999.999:8743/rcpe/`.
2. Navigate to **User Management** on the left menu.
3. Select **Domain** from the tabs.
4. Click **Create New** at the bottom of the page.
5. Enter the following details:
   - **Domain Name:** `groupnet.gr`
   - **Domain Description:** `GROUPNET Domain`
6. Click **Create**.

---

### **2. Create Users for the New Domain**
> **Note:** This step is only needed if the user does not already exist in RCPE. Check the **Users** tab to verify.

1. Navigate to **Users** in the left menu.
2. Click **Create New** at the bottom of the page.
3. Enter the username and required details provided by the customer.
   > **Note:** Do **not** add a password.
4. Click **Create**.
5. Click **Fetch All** to verify the user appears in the list.
6. Assign roles:
   - Click the **magnifying glass** next to the user.
   - Select **USERS_ASSIGN_ROLES**.
   - Add **SSO-Administrator**.
   - Click **Submit**.

---

### **3. Update SSO Configuration**
1. **Login to `unc2` as `test_r_cpe`**:
   ```bash
   ssh unc2
   su - test_r_cpe  # Use "r_cpe" for production
   ```

2. **Check RCPE Status**:
   ```bash
   trcpe-status  # Use "rcpe-status" for production
   ```

3. **Stop RCPE Service**:
   ```bash
   trcpe-stop  # Use "rcpe-stop" for production
   ```

4. **Backup Existing SSO Configuration**:
   ```bash
   cp /opt/test_r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security.xml /opt/test_r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security-backup.xml
   ```
   *(Use `/opt/r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security.xml` for production.)*

5. **Move New SSO Configuration File**:
   ```bash
   mv /home/users/ilpap/sso-security-groupnet.xml /opt/test_r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security.xml
   ```

6. **Restart RCPE and Verify Status**:
   ```bash
   trcpe-start
   trcpe-status
   ```

7. **Login to RCPE and Verify**:
   - Open `https://999.999.999.999:8743/rcpe/`.
   - Login using the shared credentials.
   - Ensure the newly created domain is visible.

---

### **4. Migrate Users to the New Domain**
1. **Backup the `SSO_USERS` Table**:
   ```bash
   mysqldump -u root -p test_r_cpe SSO_USERS --single-transaction > /tmp/SSO_USERS_BACKUP.sql
   ```

2. **Move All Users from `central-domain.root.def.gr` to `groupnet.gr`**:
   ```bash
   mysql -u root -p
   ```

   ```sql
   USE test_r_cpe;
   SHOW TABLES;
   SELECT * FROM SSO_DOMAINS LIMIT 5;  -- New domain ID should be identified (e.g., 5)
   SHOW CREATE TABLE SSO_USERS;  -- Identify old Domain_ID (e.g., 3)
   UPDATE SSO_USERS SET DOMAIN_ID=5 WHERE DOMAIN_ID=3;
   SELECT * FROM SSO_USERS WHERE DOMAIN_ID=5;
   ```

---

### **5. Delete the Old Domain**
1. **Login to RCPE with SSO Admin Access**.
2. **Navigate to User Management > Domain**.
3. **Select the Old Domain** (`central-domain.root.def.gr`).
4. **Click Delete Row(s)** at the bottom.
5. **Confirm Deletion**.

---

## Actions Taken / Expected Output
- The new `groupnet.gr` domain is created successfully.
- Users are migrated from `central-domain.root.def.gr` to `groupnet.gr`.
- RCPE is reconfigured with updated SSO settings.
- The old domain is removed from RCPE.

## Notes and Warnings
> Ensure all steps are tested in the test environment before applying changes in production.  
> The migration process will cause temporary authentication issues.  
> Always backup MySQL data before performing database modifications.

## Troubleshooting / Error Handling
- **Verify SSL Certificates are Imported**:
  ```bash
  openssl s_client -connect PVDCAHR01.groupnet.gr:636
  openssl s_client -connect PVDCLAM01.groupnet.gr:636
  ```

- **Check LDAP Search Results**:
  ```bash
  ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -W -b "dc=groupnet,dc=gr" -D "<Bind User sAMAccountName>" '(sAMAccountName=...)'
  ```

- **Check RCPE Logs**:
  ```bash
  tail -f /opt/test_r_cpe/standalone/log/server.log
  ```

- **If Users Are Not Migrated Correctly**:
  ```bash
  mysql -u root -p -e "SELECT * FROM SSO_USERS WHERE DOMAIN_ID=5;"
  ```

## References


