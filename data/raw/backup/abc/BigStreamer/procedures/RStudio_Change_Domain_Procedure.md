# RStudio Connect - Domain Change from Central to GROUPNET

## Description
This document describes the procedure for migrating the current domain from `central-domain.root.def.gr` to `groupnet`, including updating the configuration and handling user accounts.

## Prerequisites
- Verify SSL certificates for `groupnet` have been imported.
  ```bash
  openssl s_client -connect PVDCAHR01.groupnet.gr:636
  ```
  If not, import them using the formula at:
  `admin:etc/salt/salt/tls/certificate_authority/import_ca.sls`
  
- An active user from the new domain must be provided for testing.
- `/etc/hosts` file must be updated on all BigStreamer servers with the new domain.
- Perform an LDAP search to validate user existence:
  ```bash
  ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -W -b "dc=groupnet,dc=gr" -D "<Bind User sAMAccountName>" '(sAMAccountName=...)'
  ```

## Affected Systems / Scope
- **Production Server:** `unrstudio1`
- **Application URL:** `https://999.999.999.999/connect/`

---

## Procedure Steps

### **1. Backup Configuration and Database**
1. **Backup RStudio Connect configuration file**:
   ```bash
   cp -ap /etc/rstudio-connect/rstudio-connect.gcfg /etc/rstudio-connect/rstudio-connect-central.gcfg
   ```

2. **Backup the database directory**:
   ```bash
   tar -zcvf var_lib_rstudioconnect_db.tar.gz /var/lib/rstudio-connect/db/
   ```

---

### **2. Update Configuration**
1. **Stop RStudio Connect**:
   ```bash
   systemctl stop rstudio-connect
   systemctl status rstudio-connect
   ```

2. **Edit `/etc/rstudio-connect/rstudio-connect.gcfg`**  
   The new configuration file is available at:
   ```bash
   /etc/rstudio-connect/rstudio-connect-groupnet.gcfg
   ```
   Update the following values based on the LDAP search output:
   - `ServerAddress`
   - `UserSearchBaseDN`
   - `GroupSearchBaseDN`
   - `PermittedLoginGroup`
   - `BindDN`
   - `BindPassword`
   - `PublisherRoleMapping`
   - `ViewerRoleMapping`
   - `AdministratorRoleMapping`

3. **Start RStudio Connect**:
   ```bash
   systemctl start rstudio-connect
   systemctl status rstudio-connect
   ```

4. **Verify login with an active user**:
   - Open `https://999.999.999.999/connect/`
   - Login using the test user credentials.

---

### **3. Manage RStudio Connect License**
RStudio Connect has a limit of **40 active users**. If a new user needs access, but no licenses are available, an **unused user must be deleted** after customer confirmation.

#### **Delete a User**
1. **Stop RStudio Connect**:
   ```bash
   systemctl stop rstudio-connect
   systemctl status rstudio-connect
   ```

2. **List existing users**:
   ```bash
   /opt/rstudio-connect/bin/usermanager list --users
   ```

3. **Find GUID of the user to delete**:
   ```bash
   /opt/rstudio-connect/bin/usermanager list --users | grep -iv <username>
   ```

4. **Delete user**:
   ```bash
   /opt/rstudio-connect/bin/usermanager delete --users --user-guid <GUID>
   ```

5. **Verify the user is deleted**:
   - Rerun step 3 to confirm no output.
   - Log in to `https://999.999.999.999/connect/` and check under **People**.

6. **Start RStudio Connect**:
   ```bash
   systemctl start rstudio-connect
   systemctl status rstudio-connect
   ```

---

### **4. Transfer Projects and Context Between Duplicate Users**
After switching to `groupnet`, users may not see their previous projects. This occurs because user attributes such as name and email differ between `central-domain` and `groupnet`.

#### **Steps to Merge User Accounts**
1. **Stop RStudio Connect**:
   ```bash
   systemctl stop rstudio-connect
   systemctl status rstudio-connect
   ```

2. **Find IDs of duplicate users**:
   ```bash
   /opt/rstudio-connect/bin/usermanager list --users | grep -iv <username>
   ```
   *(For example, user ID in `central-domain` is `7`, and in `groupnet` is `145`.)*

3. **Transfer projects from `central-domain` to `groupnet`**:
   ```bash
   /opt/rstudio-connect/bin/usermanager transfer -source-user-id 7 -target-user-id 145
   ```

4. **Start RStudio Connect**:
   ```bash
   systemctl start rstudio-connect
   systemctl status rstudio-connect
   ```

5. **Verify Transfer**:
   - Log in to `https://999.999.999.999/connect/`
   - Navigate to **People** and check that the projects have been merged.

6. **Delete the old `central-domain` user** (as described in the previous section).

---

## Actions Taken / Expected Output
- `groupnet` is configured as the new domain.
- Users can log in and access their projects.
- If needed, unused users are removed to free licenses.
- Duplicate users from `central-domain` are merged with their `groupnet` accounts.

## Notes and Warnings
> Ensure all steps are tested before applying in production.  
> User deletion should only be performed after **explicit customer confirmation**.  
> Backup the RStudio Connect configuration and database before making changes.  

## Troubleshooting / Error Handling
- **Verify SSL Certificates are Imported**:
  ```bash
  openssl s_client -connect PVDCAHR01.groupnet.gr:636
  ```

- **Check LDAP Search Results**:
  ```bash
  ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -W -b "dc=groupnet,dc=gr" -D "<Bind User sAMAccountName>" '(sAMAccountName=...)'
  ```

- **Check RStudio Connect Logs**:
  ```bash
  tail -f /var/log/rstudio-connect.log
  ```

- **If Users Are Not Migrated Correctly**:
  ```bash
  /opt/rstudio-connect/bin/usermanager list --users
  ```

## References
- [RStudio Connect Official Documentation](https://docs.rstudio.com/connect/)
