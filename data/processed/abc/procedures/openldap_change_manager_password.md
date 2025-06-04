---
title: How to Change OpenLDAP Manager Password
description: Step-by-step instructions for changing the OpenLDAP Manager password on `kerb1` and ensuring replication with `kerb2` is functional.
owner: kpar
system: OpenLDAP
cluster: BigStreamer
services:
  - LDAP
nodes:
  - kerb1.bigdata.abc.gr
  - kerb2.bigdata.abc.gr
tags:
  - ldap
  - password
  - openldap
  - kerb
  - manager
  - authentication
  - security
status: verified
last_updated: 2024-05-01
related_docs:
  - KnowledgeBase/prodsyspasswd.kdbx
---
This procedure explains how to securely change the OpenLDAP Manager password on kerb1, update both the config and data databases via LDIF files, and verify replication and authentication using both CLI and the phpLDAPadmin web UI.
# OpenLDAP Manager Password Change
For every ldasearch the password of `Manager` is [here](KnowledgeBase/prodsyspasswd.kdbx)
## Step 1: Login to LDAP Node
Login into the primary LDAP node (`kerb1`) with root access.
```bash
ssh kerb1
sudo -i
```
## Step 2: Generate New SSHA Password Hash
Use `slappasswd` to create a new SSHA-encoded password for the LDAP Manager account.
```bash
slappasswd -h {SSHA}
```
## Step 3: Store the output 
The output will be start with something like `{SSHA}xxxxxxx` 
## Step 4: Create LDIF Files to Apply Password Change
Create two LDIF files: one for the config database and one for the BDB (data) database.
### 4a. LDIF for config database
```bash
vi changepwconfig.ldif
dn: olcDatabase={0}config,cn=config
changetype: modify
replace: olcRootPW
olcRootPW: paste the output from step `3`
```
### 4b. LDIF for manager database
```bash
vi changepwmanager.ldif
dn: olcDatabase={2}bdb,cn=config
changetype: modify
replace: olcRootPW
olcRootPW: paste the output from step `3`
```
## Step 5: Backup Existing Configuration
Use `slapcat` to export the current config and data for recovery purposes.
```bash
slapcat -n 0 -l config.ldif
slapcat -n 2 -l data.ldif
```
## Step 6: Apply Password Changes
Use `ldapmodify` with the generated LDIF files to apply the password change.
```bash
ldapmodify -H ldapi:// -Y EXTERNAL -f changepwmanager.ldif
ldapmodify -H ldapi:// -Y EXTERNAL -f changepwconfig.ldif
```
## Step 7: Validate the New Password
Test that the new Manager password works both via CLI and web UI on `kerb1` and `kerb2`.
### 7a. Command-Line Verification
For `kerb1`. Where `uid` add a ldap user. e.g your ldap username:
```bash
ldapsearch -H ldaps://kerb1.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"  'uid=xxxx'
```
For `kerb2`. Where `uid` add a ldap user. e.g your ldap username::
```bash
ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"  'uid=xxxx'
```
### 7b. Web UI Verification
Login into `admin` node as `root`:
Open firefox
```bash
firefox
```
phpldapadmin link: https://kerb1.bigdata.abc.gr/phpldapadmin/
Try to connect with the new `Manager` password