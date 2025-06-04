---
title: "Fixing OpenLDAP Replication Issues"
description: "Step-by-step instructions for resolving OpenLDAP replication failures between kerb1 and kerb2, including password updates, slapcat/slapadd procedures, and verification via ldapsearch."
tags:
  - openldap
  - replication
  - ldap
  - slapcat
  - slapadd
  - kerb1
  - kerb2
  - phpldapadmin
  - ldapsearch
  - slapd
  - sync
  - mirror mode
  - user creation
  - credentials
  - config.ldif
  - data.ldif
  - restore ldap
  - slapd.d
---
# How to fix openldap replication
This guide documents how to fix broken OpenLDAP replication between kerb1 and kerb2, addressing two scenarios: a Manager password change or corruption due to events like power outages. It includes configuration updates, slapcat/slapadd restore steps, verification procedures, and UI-based user creation checks via phpLDAPadmin.
The broken replication between `kerb1`/`kerb2` could happened in case any of the below cases appeared/happened.
- Case 1: You changed the `Manager` password of openldap instance
- Case 2: Replication broken for any other reason (power outage etc) between `kerb1` and `kerb2`
For every ldasearch the password of `Manager` is [here](KnowledgeBase/prodsyspasswd.kdbx)
## For Case 1 follow the below steps:
Login into kerb1 node as root
```bash
ssh kerb1
sudo -i
```
Backup:
```bash
slapcat -n 0 -l config.ldif
slapcat -n 2 -l data.ldif
```
Create ldif file replication fix
```bash
vi replication_config.ldif
dn: olcDatabase={0}config,cn=config
changetype:modify
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
changetype:modify
replace: olcSyncrepl
olcSyncrepl: rid=003
  provider=ldaps://kerb1.bigdata.abc.gr/
  binddn="cn=Manager,dc=bigdata,dc=abc,dc=gr"
  bindmethod=simple
  credentials=`new password`
  searchbase="dc=bigdata,dc=abc,dc=gr"
  type=refreshAndPersist
  retry="5 5 300 +"
  timeout=1
olcSyncrepl: rid=004
  provider=ldaps://kerb2.bigdata.abc.gr/
  binddn="cn=Manager,dc=bigdata,dc=abc,dc=gr"
  bindmethod=simple
  credentials=`new password`
  searchbase="dc=bigdata,dc=abc,dc=gr"
  type=refreshAndPersist
  retry="5 5 300 +"
  timeout=1
add: olcMirrorMode
olcMirrorMode: TRUE
```
Fix the replication:
```bash
ldapmodify  -H ldaps://kerb1.bigdata.abc.gr -D "cn=config" -W -f replication_config.ldif
ldapmodify  -H ldaps://kerb2.bigdata.abc.gr -D "cn=config" -W -f replication_config.ldif
```
Checks:
Create a new user on ldap kerb1 via `UI` with name `testuser`:
Login into admin node as root:
Open firefox
```bash
firefox
```
phpldapadmin link: (https://kerb1.bigdata.abc.gr/phpldapadmin/)
## Steps to create an ldap user
1. Connect with username `cn=Manager,dc=bigdata,dc=abc,dc=gr` and password from `kdbx` file.
2. Expand tree `people`
3. Click `create a new entry here`
4. The type of account will be `User account`
5. Fill all the empty boxes. 
6. The user will be `no login` and the group/gid `disabled`
7. Create object
After succesfully creation of `testuser` check if exist on `kerb2` from the dropdown menu or via ldapsearch
```bash
ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"  'uid=testuser'
```
If user exist then replication fixed. Just delete the `testuser`.
## Steps to delete an ldap user
1. Connect with username `cn=Manager,dc=bigdata,dc=abc,dc=gr` and password from `kdbx` file.
2. Expand tree `people`
3. Check the new user and from the right bar click `delete this entry`
## For Case 2 follow the below steps:
Identify which `kerb` ldap instance has the issue. For example check if they had the same amount of `users` and `groups` with `ldapsearch` commands from checks
From the `kerb` ldap instance without corruption :
```bash
slapcat -n 0  config.ldif
slapcat -n 1 data.ldif
scp *.ldif `ldap_instance_with_corruption`:/tmp
```
Go to corrupted `kerb` instance:
Backup:
```bash
cp -rp /etc/openldap/ /tmp/openldap.bak
cp -rp /var/lib/ldap/ /tmp
```
Clear:
```bash
systemctl stop slapd
systemctl status slapd
cd /etc/openldap/
rm –Rf slapd.d
cd /etc/openldap
mkdir slapd.d
cd /var/lib/ldap/
rm –Rf *
```
Restore:
```bash
slapadd -n 0 -F /etc/openldap/slapd.d -l /tmp/config.ldif
slapadd -n 2 -F /etc/openldap/slapd.d -l /tmp/data.ldif -w
```
Ownership:
```bash
chown -R ldap:ldap /var/lib/ldap
```
Start `slapd` service:
```bash
systemctl start slapd
systemctl status slapd
```
Checks:
Create a new user on ldap kerb1 via `UI` with name `testuser`:
The procedure to create a new user described [here](/KnowledgeBase/abc/BigStreamer/supportDocuments/procedures/openldap_change_manager_password.md)
Login into admin node as root:
Open firefox
```bash
firefox
```
phpldapadmin link: (https://kerb1.bigdata.abc.gr/phpldapadmin/)
After successfully creation of `testuser` check if exist on `kerb2` from the dropdown menu or via ldapsearch
```bash
ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"  'uid=testuser'
```
If user exist then replication fixed. Just delete the `testuser`.
The procedure to delete a new user described [here](/KnowledgeBase/abc/BigStreamer/supportDocuments/procedures/openldap_change_manager_password.md)
---
tags:
  - ldap
  - openldap
  - kerberos
  - slapcat
  - slapadd
  - phpldapadmin
  - ldap replication
  - directory service
  - slapd
  - user management
  - config.ldif
  - data.ldif
---