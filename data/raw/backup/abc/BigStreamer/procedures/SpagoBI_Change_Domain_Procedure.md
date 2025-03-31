# SpagoBI Integration with GROUPNET

## Description
This document describes the procedure for migrating the current domain from `central-domain.root.def.gr` to `groupnet`, including updating configuration and handling user accounts.

## Prerequisites
1. **Verify SSL Certificates for GROUPNET**  
   Check if the SSL certificates have already been imported:
   ```bash
   openssl s_client -connect PVDCAHR01.groupnet.gr:636
   ```
   If not, import them using the formula:
   `admin:etc/salt/salt/tls/certificate_authority/import_ca.sls`

2. **Obtain Required User Information**
   - An active user from the new domain for testing (e.g., `enomikos`).
   - A **bind user** for GROUPNET domain configuration.

3. **Update `/etc/hosts` File**  
   Ensure the `/etc/hosts` file on `un5` and other BigStreamer servers includes the new domain.

4. **Perform an LDAP Search for the Bind User**
   ```bash
   ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -D "t1-svc-cnebind" -W -b "dc=groupnet,dc=gr" '(sAMAccountName=enomikos)'
   ```

## Affected Systems / Scope
- **Production Server:** `un5.bigdata.abc.gr`
- **Application URL:** `https://cne.def.gr/SpagoBI`
- **Reverse Proxy Server:** `un1.bigdata.abc.gr`
- **Database Server:** `db01`

---

## Procedure Steps

### **1. Backup Existing Configuration**
1. **Backup SpagoBI MySQL Database**:
   ```bash
   mysqldump -u root -p spagobi --single-transaction > /tmp/spagobi.sql
   ```

2. **Backup `ldap_authorizations.xml`**:
   ```bash
   cp -ap /usr/lib/spagobi/webapps/SpagoBIProject/WEB-INF/conf/webapp/ldap_authorizations.xml /usr/lib/spagobi/webapps/SpagoBIProject/WEB-INF/conf/webapp/ldap_authorizations-central.xml
   ```

3. **Backup HAProxy Configuration**:
   ```bash
   cp -ap /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.bak
   ```

---

### **2. Create and Validate GROUPNET User in SpagoBI**
1. **Login to SpagoBI** at `https://cne.def.gr/SpagoBI`
2. **Create GROUPNET User (`enomikos`)**
   - Navigate to **User Management**
   - Click **Add**
   - Fill in the User ID and Full Name
   - Assign necessary roles
   - Save

3. **Verify User Creation in the Database**
   ```bash
   mysql -u spagobi -p
   use spagobi;
   show tables;
   select * FROM SBI_USER WHERE USER_ID='enomikos@groupnet';
   ```

---

### **3. Update SpagoBI LDAP Configuration**
1. **Stop SpagoBI Process**:
   ```bash
   docker stop prod-spagobi-7.0.105
   ```

2. **Edit LDAP Configuration File**:
   Modify `/usr/lib/spagobi/webapps/SpagoBIProject/WEB-INF/conf/webapp/ldap_authorizations.xml`
   ```xml
   <!--  SERVER -->
   <HOST>un1.bigdata.abc.gr</HOST>
   <PORT>863</PORT>        
   <ADMIN_USER>replace_with_name_of_admin</ADMIN_USER>
   <ADMIN_PSW>replace_with_password</ADMIN_PSW> <!-- password in clear text -->
   <BASE_DN>dc=groupnet,dc=gr</BASE_DN> <!-- base domain -->
   ```

---

### **4. Update HAProxy Configuration for GROUPNET**
1. **Modify HAProxy Configuration (`un1:/etc/haproxy/haproxy.cfg`)**:
   ```bash
   listen def-ad-ldaps
       bind *:863 ssl crt /opt/security/haproxy/node.pem
       mode tcp
       balance source
       server def_ad1 PVDCAHR01.groupnet.gr:636 ssl check ca-file /etc/ssl/certs/ca-bundle.crt
   ```

2. **Validate and Apply HAProxy Configuration**:
   ```bash
   haproxy -f /etc/haproxy/haproxy.cfg -c
   systemctl reload haproxy
   systemctl status haproxy
   ```

---

### **5. Restart and Verify SpagoBI**
1. **Start SpagoBI Application**:
   ```bash
   docker start prod-spagobi-7.0.105
   ```

2. **Verify Login**:
   - Attempt to log in as `enomikos`.
   - If successful, proceed to update existing users.

---

### **6. Migrate Existing Users to GROUPNET**
1. **Move All Users from `central-domain.root.def.gr` to `groupnet.gr`**:
   ```bash
   mysql -u root -p
   use spagobi;
   select * from SBI_USER WHERE USER_ID LIKE '%@central-domain%'; # Check users in central-domain
   UPDATE SBI_USER SET USER_ID = REPLACE(USER_ID,'@central-domain','@groupnet') WHERE USER_ID LIKE '%@central-domain%';
   select * from SBI_USER WHERE USER_ID LIKE '%@central-domain%'; # Ensure all users moved
   ```

2. **Test Migration with a Single User Before Full Migration**:
   ```bash
   UPDATE SBI_USER SET USER_ID = REPLACE(USER_ID,'@groupnet.gr','@groupnet') WHERE USER_ID LIKE '%enomikos@groupnet.gr%';
   select * from SBI_USER WHERE USER_ID LIKE '%enomikos@groupnet.gr%';
   ```

---

## Actions Taken / Expected Output
- **GROUPNET domain successfully integrated** with SpagoBI.
- **New users from GROUPNET can log in** to SpagoBI.
- **All existing users** migrated from `central-domain.root.def.gr` to `groupnet.gr`.

## Notes and Warnings
> **Ensure all steps are tested before applying in production.**  
> **User migration should be done cautiously.** Test with a single user before migrating all users.  
> **HAProxy configuration changes require a reload to take effect.**  

## Troubleshooting / Error Handling
- **Check if GROUPNET SSL Certificates are Imported**:
  ```bash
  openssl s_client -connect PVDCAHR01.groupnet.gr:636
  ```

- **Verify LDAP Search Results**:
  ```bash
  ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -D "t1-svc-cnebind" -W -b "dc=groupnet,dc=gr" '(sAMAccountName=enomikos)'
  ```

- **Check HAProxy Logs**:
  ```bash
  tail -f /var/log/haproxy.log
  ```

- **Restart SpagoBI if Issues Occur**:
  ```bash
  docker restart prod-spagobi-7.0.105
  ```

- **If Users Are Not Migrated Correctly**:
  ```bash
  mysql -u root -p
  use spagobi;
  select * from SBI_USER WHERE USER_ID LIKE '%@central-domain%';
  ```

## References
- [SpagoBI Official Documentation](https://www.spagobi.org/)

