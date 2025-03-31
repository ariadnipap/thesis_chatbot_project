# How to Change OpenLDAP Manager Password

## Description
This procedure outlines the steps required to change the OpenLDAP `Manager` password on the `kerb1` node.

## Prerequisites
- SSH access to `kerb1` as root.
- Knowledge of the existing `Manager` password (stored in `KnowledgeBase/prodsyspasswd.kdbx`).
- Permissions to modify LDAP configuration.
- Installed OpenLDAP utilities (`slapd`, `ldapmodify`).

## Affected Systems / Scope
- **OpenLDAP Server:** `kerb1.bigdata.abc.gr`
- **Configuration Files:**
  - `config.ldif`
  - `data.ldif`
- **Service Impact:** LDAP authentication may be temporarily disrupted during changes.

---

## Procedure Steps

### **1. Login to `kerb1` as Root**
```bash
ssh kerb1
sudo -i
```

---

### **2. Generate a New SSHA Password**
```bash
slappasswd -h {SSHA}
```
- **Expected Output:** `{SSHA}xxxxxxx`
- **Store this output** for later use.

---

### **3. Create LDIF Files to Update the Password**
#### **a. Modify Configuration Password**
```bash
vi changepwconfig.ldif
```
- Add the following:
  ```bash
  dn: olcDatabase={0}config,cn=config
  changetype: modify
  replace: olcRootPW
  olcRootPW: {SSHA}xxxxxxx
  ```
  *(Replace `{SSHA}xxxxxxx` with the output from Step 2.)*

#### **b. Modify Manager Password**
```bash
vi changepwmanager.ldif
```
- Add the following:
  ```bash
  dn: olcDatabase={2}bdb,cn=config
  changetype: modify
  replace: olcRootPW
  olcRootPW: {SSHA}xxxxxxx
  ```
  *(Replace `{SSHA}xxxxxxx` with the output from Step 2.)*

---

### **4. Backup OpenLDAP Configuration and Data**
```bash
slapcat -n 0 -l config.ldif
slapcat -n 2 -l data.ldif
```

---

### **5. Apply the New Password**
```bash
ldapmodify -H ldapi:// -Y EXTERNAL -f changepwmanager.ldif
ldapmodify -H ldapi:// -Y EXTERNAL -f changepwconfig.ldif
```

---

### **6. Verification**
#### **a. Check via Command Line**
- **For `kerb1`**: (Replace `xxxx` with a valid LDAP username)
  ```bash
  ldapsearch -H ldaps://kerb1.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr" 'uid=xxxx'
  ```
- **For `kerb2`**: (Replace `xxxx` with a valid LDAP username)
  ```bash
  ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr" 'uid=xxxx'
  ```

#### **b. Check via UI**
1. **Login to the `admin` node as root**:
   ```bash
   ssh root@admin-node
   ```
2. **Open Firefox**:
   ```bash
   firefox
   ```
3. **Navigate to**:  
   ```
   https://kerb1.bigdata.abc.gr/phpldapadmin/
   ```
4. **Attempt to login using the new `Manager` password**.

---

## Actions Taken / Expected Output
- Successfully changed the OpenLDAP `Manager` password.
- Verified access using both command-line and web UI.
- Ensured LDAP authentication is working without issues.

## Notes and Warnings
> Ensure that you **store the new password securely**.  
> Backup `config.ldif` and `data.ldif` before making changes.  
> If authentication issues occur, rollback using the backup files.

## Troubleshooting / Error Handling
- **If the password change does not apply:**
  ```bash
  cat changepwconfig.ldif
  cat changepwmanager.ldif
  ```
- **If LDAP authentication fails after the change:**
  ```bash
  systemctl restart slapd
  ```
- **Check logs for errors:**
  ```bash
  journalctl -xe -u slapd
  tail -f /var/log/slapd.log
  ```

## References
- [phpldapadmin](https://kerb1.bigdata.abc.gr/phpldapadmin/)

