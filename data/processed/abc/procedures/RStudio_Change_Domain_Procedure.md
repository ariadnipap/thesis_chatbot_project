---
title: RStudio Connect - Migrate to GROUPNET Domain
description: Procedure for migrating RStudio Connect LDAP authentication from central-domain.root.def.gr to GROUPNET domain including certificate verification, configuration changes, user license management, and resolving duplicate users.
tags:
  - rstudio-connect
  - ldap
  - groupnet
  - user-migration
  - license-management
  - project-transfer
  - domain-migration
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  system: unrstudio1
  domain_from: central-domain.root.def.gr
  domain_to: groupnet
  login_page: https://999.999.999.999/connect/
---
# RStudio - Change Domain Procedure
## Description
This document describes the procedure of changing current domain from `central-domain.root.def.gr` to `groupnet` along with their users
### Server
PVDCAHR01.groupnet.gr
### Useful info
PROD
- https://999.999.999.999/connect/
- unrstudio1
### Prerequisites
Verify if GROUPNET LDAP SSL certificates are already trusted by the server
1. Check if the ssl certificates of the groupnet have already been imported
```bash
[root@unrstudio1 ~]# openssl s_client -connect PVDCAHR01.groupnet.gr:636
```
If they are not been imported, you should import them using formual at `admin:etc/salt/salt/tls/certificate_authority/import_ca.sls`.
2. Customer should send an active user that belongs to the new domain for testing 
3. `/etc/hosts` file must be updated to all  BigStreamer servers with the new domain 
4. Perfom an ldap search for the given user:
```
ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -W -b "dc=groupnet,dc=gr" -D "<Bind User sAMAccountName>" '(sAMAccountName=...)'
```
### Backup
1. Back up `rstudio-connect-central.gcfg`
```bash
[root@unrstudio1 ~]# cp -ap /etc/rstudio-connect/rstudio-connect.gcfg /etc/rstudio-connect/rstudio-connect-central.gcfg
```
2. Backup database directory `/var/lib/rstudio-connect/db/`
```bash
[root@unrstudio1 ~]# tar -zcvf var_lib_rstudioconnect_db.tar.gz /var/lib/rstudio-connect/db/
```
### Update configuration
Update RStudio Connect config file with new LDAP bind credentials and search base DNs
1. Stop rstudio-connect
```bash
[root@unrstudio1 ~]# systemctl status rstudio-connect
[root@unrstudio1 ~]# systemctl stop rstudio-connect
[root@unrstudio1 ~]# systemctl status rstudio-connect
```
2. Edit `/etc/rstudio-connect/rstudio-connect.gcfg`
You can find new configuration at: `[root@unrstudio1 ~]# /etc/rstudio-connect/rstudio-connect-groupnet.gcfg`
Values that must be changed:
- ServerAddress
- UserSearchBaseDN
- GroupSearchBaseDN
- PermittedLoginGroup #This value must be set according to the ouput of previous ldap search
- BindDN
- BindPassword
- PublisherRoleMapping #This value must be set according to the ouput of previous ldap search
- ViewerRoleMapping #This value must be set according to the ouput of previous ldap search
- AdministratorRoleMapping #This value must be set according to the ouput of previous ldap search
3. Start rstudio-connect
```bash
[root@unrstudio1 ~]# systemctl status rstudio-connect
[root@unrstudio1 ~]# systemctl start rstudio-connect
[root@unrstudio1 ~]# systemctl status rstudio-connect
```
4. Login to https://999.999.999.999/connect/ with the active user.
### Rstudio Lisence
RStudio Connect has a limit for the number of active users it can serve. Currently, the license we have, can serve only 40 active users.
What can you do though in case you want to add another user but there are not free licenses? 
**Only after getting customer's confirmation you can delete another user that it is not used**
### Delete user
Clean up a deactivated or duplicate user from RStudio Connect user base
1. In order to use `/opt/rstudio-connect/bin/usermanager list --users` command you must first stop RStudio connect
```bash
[root@unrstudio1 ~]# systemctl stop rstudio-connect
[root@unrstudio1 ~]# systemctl status rstudio-connect
```
2. List existing users
```bash
[root@unrstudio1 ~]# /opt/rstudio-connect/bin/usermanager list --users
```
3. Let's assume that we want to delete `dsimantir` account. Let's find his GUID.
```bash
[root@unrstudio1 ~]# /opt/rstudio-connect/bin/usermanager list --users | grep -iv dsimantir
```
Output must be something like below:
| GUID  |  ID | Username   |  First |  Last  |  Email   |   Role |  DN  | UniqueID  |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| e633e5b9-cbc3-4fb3-8c3b-19ba4aa617b7  | 16  |  dsimantir  |   |   | dsimantir@uatdef.gr  | publisher   | CN=dsimantir,OU=def_users,DC=uatdef,DC=gr  |  EQGFgRGDt0KZ9sAipdlzhw== |
4. Delete user
```bash
[root@unrstudio1 ~]# /opt/rstudio-connect/bin/usermanager delete --users --user-guid e633e5b9-cbc3-4fb3-8c3b-19ba4aa617b7
```
5. Verify that user is deleted by re-running step 3 and make sure that there is no output.
6. Start rstudio-connect
```bash
[root@unrstudio1 ~]# systemctl start rstudio-connect
[root@unrstudio1 ~]# systemctl status rstudio-connect
```
7. You can also verify that the user is deleted by login to https://999.999.999.999/connect/ with the active user account > People 
### Transfer projects/context from one user to another in case of duplicate users
Transfer user ownership and projects from central-domain to GROUPNET in case of duplicated accounts
In our case, when we changed `central-domain` to `groupnet` we noticed that when users logged in to the `groupnet` domain they were not able to see their projects.
That issue occurred due to the fact that name, email and other attributes where different to `central` and `groupnet`. For example:
- Chrisostomos Charisis, ccharisis@def.gr -> central domain
- Chrisostomos Charisis, CCHARISIS@abc.GR -> groupnet domain
> Ndef: Login to https://999.999.999.999/connect/ with the active user account > People > Search for the specific user and check the contents of the duplicate user
As a result, the user was considered as different account and a different registration was created.
So, how can merge those two accounts? 
1. Stop rstudio-connect
```bash
[root@unrstudio1 ~]# systemctl stop rstudio-connect
[root@unrstudio1 ~]# systemctl status rstudio-connect
```
2. Find id of above duplicate users:
```bash
[root@unrstudio1 ~]# /opt/rstudio-connect/bin/usermanager list --users | grep -iv ccharisis
```
Let's assume that the id of ccharisis in central domain is 7 and the id of ccharisis in groupnet is 145
3. Transfer account from `central-domain` to `groupnet` using following command:
```bash
[root@unrstudio1 ~]# /opt/rstudio-connect/bin/usermanager transfer -source-user-id 7 -target-user-id 145
```
4. Start rstudio-connect
```bash
[root@unrstudio1 ~]# systemctl start rstudio-connect
[root@unrstudio1 ~]# systemctl status rstudio-connect
```
5.  Login to https://999.999.999.999/connect/ with the active user account > People > Search for the specific user and check the contents of the duplicate user have been transferred
6. Delete user that belongs to `central-domain` as described in previous section