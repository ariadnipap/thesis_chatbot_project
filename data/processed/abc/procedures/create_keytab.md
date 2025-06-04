---
title: "Create a Kerberos Keytab in NYMA"
description: "Step-by-step guide to create a Kerberos keytab for a user in the NYMA environment using kadmin.local, transfer it to un2, and set ownership."
tags:
  - kerberos
  - keytab
  - nyma
  - kadmin
  - authentication
  - principal
  - un2
  - linux
  - hadoop
  - access control
---
# How to create a keytab in NYMA
This procedure explains how to create a Kerberos keytab file for a user in the NYMA environment and deploy it to the appropriate node with correct permissions.
## Step 1: Login to the Kerberos server (kerb1) as root
```bash
ssh kerb1
sudo -i
```
## Step 2: Open the Kerberos admin interface
```bash
kadmin.local
```
## Step 3: Check if the principal exists
```bash
listprincs <username>@CNE.abc.GR
```
## Step 4: Create the principal (if missing)
```bash
addprinc <username>CNE.abc.GR
```
## Step 5: Generate the keytab file
```bash
ktadd -k /tmp/<username>.keytab -norandkey <username>@CNE.abc.GR
```
## Step 6: Copy the keytab to un2 node
```bash
scp -p /tmp/<username>.keytab un2:/tmp
```
## Step 7: Move the keytab and set permissions
```bash
ssh un2
sudo -i
cp -p /tmp/<username>.keytab /home/users/skokkoris/
chown skokkoris. /home/users/skokkoris/<username>.keytab
```