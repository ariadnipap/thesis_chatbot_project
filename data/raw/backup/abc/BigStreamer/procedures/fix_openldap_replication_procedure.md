# How to Fix OpenLDAP Replication

## Description
This procedure outlines the steps to fix broken OpenLDAP replication between `kerb1` and `kerb2`, which may occur due to a password change or other issues such as power outages.

## Prerequisites
- SSH access to `kerb1` and `kerb2` as `root`.
- OpenLDAP administrator privileges.
- Knowledge of the `Manager` password stored in the `KnowledgeBase/prodsyspasswd.kdbx` file.

## Procedure Steps

### **Case 1: Replication Broken Due to Manager Password Change**

#### 1. Login into `kerb1` as Root
```bash
ssh kerb1
sudo -i
```

#### 2. Backup Existing Data
```bash
slapcat -n 0 -l config.ldif
slapcat -n 2 -l data.ldif
```

#### 3. Create a Replication Fix LDIF File
- Create and edit the `replication_config.ldif` file:
  ```bash
  vi replication_config.ldif
  ```
- Add the following content, replacing `"new password"` with the actual password:
  ```yaml
  dn: olcDatabase={0}config,cn=config
  changetype: modify
  replace: olcSyncrepl
  olcSyncrepl: rid=001
    provider=ldaps://kerb1.bigdata.abc.gr/
    binddn="cn=config"
    bindmethod=simple
    credentials="new password"
    searchbase="cn=config"
    type=refreshAndPersist
    retry="5 5 300 +"
    timeout=1
  olcSyncrepl: rid=002
    provider=ldaps://kerb2.bigdata.abc.gr/
    binddn="cn=config"
    bindmethod=simple
    credentials="new password"
    searchbase="cn=config"
    type=refreshAndPersist
    retry="5 5 300 +"
    timeout=1

  add: olcMirrorMode
  olcMirrorMode: TRUE

  dn: olcDatabase={2}bdb,cn=config
  changetype: modify
  replace: olcSyncrepl
  olcSyncrepl: rid=003
    provider=ldaps://kerb1.bigdata.abc.gr/
    binddn="cn=Manager,dc=bigdata,dc=abc,dc=gr"
    bindmethod=simple
    credentials="new password"
    searchbase="dc=bigdata,dc=abc,dc=gr"
    type=refreshAndPersist
    retry="5 5 300 +"
    timeout=1
  olcSyncrepl: rid=004
    provider=ldaps://kerb2.bigdata.abc.gr/
    binddn="cn=Manager,dc=bigdata,dc=abc,dc=gr"
    bindmethod=simple
    credentials="new password"
    searchbase="dc=bigdata,dc=abc,dc=gr"
    type=refreshAndPersist
    retry="5 5 300 +"
    timeout=1

  add: olcMirrorMode
  olcMirrorMode: TRUE
  ```

#### 4. Apply the Replication Fix
```bash
ldapmodify -H ldaps://kerb1.bigdata.abc.gr -D "cn=config" -W -f replication_config.ldif
ldapmodify -H ldaps://kerb2.bigdata.abc.gr -D "cn=config" -W -f replication_config.ldif
```

#### 5. Verify Replication
- Create a new LDAP user `testuser` in `kerb1` using the **PHP LDAP Admin UI**:
  ```
  https://kerb1.bigdata.abc.gr/phpldapadmin/
  ```
- Search for the new user on `kerb2`:
  ```bash
  ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"  'uid=testuser'
  ```
- If `testuser` exists, replication is fixed. Delete `testuser` from the LDAP admin UI.

---

### **Case 2: Replication Broken Due to Other Issues (Power Outage, etc.)**

#### 1. Identify the Corrupted LDAP Instance
- Compare the number of users and groups on both instances:
  ```bash
  ldapsearch -H ldaps://kerb1.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"
  ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"
  ```
- If the output differs, one of the LDAP instances is corrupted.

#### 2. Backup the Healthy LDAP Instance
```bash
slapcat -n 0 -l config.ldif
slapcat -n 1 -l data.ldif
scp *.ldif ldap_instance_with_corruption:/tmp
```

#### 3. Backup and Clear the Corrupted Instance
- Login to the corrupted instance:
  ```bash
  ssh ldap_instance_with_corruption
  sudo -i
  ```
- Backup existing LDAP data:
  ```bash
  cp -rp /etc/openldap/ /tmp/openldap.bak
  cp -rp /var/lib/ldap/ /tmp
  ```
- Stop the LDAP service:
  ```bash
  systemctl stop slapd
  systemctl status slapd
  ```
- Clear corrupted data:
  ```bash
  cd /etc/openldap/
  rm -Rf slapd.d
  mkdir slapd.d
  cd /var/lib/ldap/
  rm -Rf *
  ```

#### 4. Restore Data from the Healthy Instance
```bash
slapadd -n 0 -F /etc/openldap/slapd.d -l /tmp/config.ldif
slapadd -n 2 -F /etc/openldap/slapd.d -l /tmp/data.ldif -w
```

#### 5. Set Ownership and Restart LDAP Service
```bash
chown -R ldap:ldap /var/lib/ldap
systemctl start slapd
systemctl status slapd
```

#### 6. Verify Replication
- Create a test user in `kerb1` using the PHP LDAP Admin UI.
- Check if the user exists in `kerb2`:
  ```bash
  ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr" 'uid=testuser'
  ```
- If `testuser` exists, replication is fixed.

## Actions Taken / Expected Output
- OpenLDAP replication should be restored between `kerb1` and `kerb2`.
- New users created in `kerb1` should be visible in `kerb2`.
- If Case 2 was applied, the corrupted LDAP instance should be restored.

## Notes and Warnings
> Always back up LDAP data before applying changes.  
> Ensure the correct `Manager` password is used when modifying configurations.

## Affected Systems / Scope
- OpenLDAP instances on `kerb1` and `kerb2`.

## Troubleshooting / Error Handling
- If replication is still broken, check logs:
  ```bash
  tail -f /var/log/openldap.log
  ```
- Verify LDAP service status:
  ```bash
  systemctl status slapd
  ```
- If `slapadd` fails, check file permissions:
  ```bash
  ls -lah /var/lib/ldap/
  ```

## References
