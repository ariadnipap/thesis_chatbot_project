---
title: SpagoBI Integration with GROUPNET Domain
description: Procedure for migrating SpagoBI authentication from central-domain.root.def.gr to GROUPNET, including LDAP search, HAProxy update, config changes, and user migration in the spagobi MySQL database.
tags:
  - spagobi
  - groupnet
  - ldap
  - haproxy
  - user-migration
  - domain-change
  - mysql
  - authentication
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  systems:
    - un5.bigdata.abc.gr
    - db01
    - un1 (HAProxy)
  domains:
    from: central-domain.root.def.gr
    to: groupnet
  app_url: https://cne.def.gr/SpagoBI
  bind_server: PVDCAHR01.groupnet.gr
---
# abc - [One Domain] SpagoBI integration with GROUPNET
This document describes the procedure of changing current domain from `central-domain.root.def.gr` to `groupnet` along with their users.
Server to use: PVDCAHR01.groupnet.gr
Prod Server: un5.bigdata.abc.gr
URL: https://cne.def.gr/SpagoBI
999.999.999.999 cne.def.gr cne
### Prerequisites
Verify if GROUPNET LDAP server's SSL certificate is already trusted by un5
1. Check if the ssl certificates of the groupnet have already been imported
```bash
[root@un5 ~]# openssl s_client -connect PVDCAHR01.groupnet.gr:636
```
If it is not been imported, you should import them using formula  `admin:etc/salt/salt/tls/certificate_authority/import_ca.sls`.
2. Customer should send an active user that belongs to the new domain so we can verify that the change is succesfully made. 
Vaggos username in our case (enomikos)
3. Customer should also send a bind user that we will use for groupnet domain configuration.
4. `/etc/hosts` file at `un5` must be updated to all  BigStreamer servers with the new domain 
5. Perfom an ldap search for the given bind user. 
```bash
[root@unrstudio1 ~]# ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -D "t1-svc-cnebind" -W -b "dc=groupnet,dc=gr" '(sAMAccountName=enomikos)'
```
### Backup
Backup current SpagoBI user database in case rollback is needed
1. Backup spagobi mysql database:
```bash
[root@db01 ~]# mysqldump -u root -p spagobi --single-transaction > /tmp/spagobi.sql
```
2. Back up `ldap_authorizations.xml`:
```bash
[root@un5 ~]# cp -ap /usr/lib/spagobi/webapps/SpagoBIProject/WEB-INF/conf/webapp/ldap_authorizations.xml /usr/lib/spagobi/webapps/SpagoBIProject/WEB-INF/conf/webapp/ldap_authorizations-central.xml
```
3. Back up haproxy:
```bash
[root@un1 ~]# cp -ap /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.bak
```
### Actions
1. Login to `https://cne.def.gr/SpagoBI` with the credentials you have and create groupnet user for user `enomikos`:
- User Management
- Click on **Add**
- Fill in with the user ID and full name
- Add roles
- Save
2. Verify that the user is successfully created using following commands:
```bash
[root@db01 ~]# mysql -u spagobi -p;
mysql> use spagobi;
mysql> show tables;
mysql> select * FROM SBI_USER WHERE USER_ID='enomikos@groupnet';
```
3. Stop SpagoBI process:
```bash
[root@un5 ~]# docker stop prod-spagobi-7.0.105
```
4. Update SpagoBI LDAP config to use new GROUPNET bind credentials and base DN. Edit the following lines at `un5:/usr/lib/spagobi/webapps/SpagoBIProject/WEB-INF/conf/webapp/ldap_authorizations.xml`:
```bash
<!--  SERVER -->
                <HOST>un1.bigdata.abc.gr</HOST>
                <PORT>863</PORT>        
                <ADMIN_USER>replace_with_name_of_admin</ADMIN_USER>
                <ADMIN_PSW>replace_with_password</ADMIN_PSW> <!-- password in clear text -->
                <BASE_DN>dc=groupnet,dc=gr</BASE_DN> <!-- base domain, if any -->
```
5. Expose GROUPNET AD through HAProxy with LDAPS support to be reachable from SpagoBI. Update reverse proxy at `un1` so that Groupnet AD can be reached directly from spagobi app.
Add the following at `un1:/etc/haproxy/haproxy.cfg`
```bash
listen def-ad-ldaps
    bind *:863 ssl crt /opt/security/haproxy/node.pem
    mode tcp
    balance     source
    server def_ad1 PVDCAHR01.groupnet.gr:636 ssl check ca-file /etc/ssl/certs/ca-bundle.crt
```
6. Test and reload haproxy in order changes to take effect
```bash
[root@un1 ~]# haproxy -f /etc/haproxy/haproxy.cfg -c
[root@un1 ~]# systemctl reload haproxy
[root@un1 ~]# systemctl status haproxy
```
7. Start SpagoBI app:
```bash
[root@un5 ~]# docker start prod-spagobi-7.0.105
```
8. Check if `enomikos` can sign in. If yes, then go to the next step
9. Migrate all users in SpagoBI MySQL DB from central-domain to groupnet. Move all users that have domain `central-domain.root.def.gr` to `groupnet.gr`
```bash
[root@db01 ~]# mysql -u root -p;
mysql> use spagobi;
select * from SBI_USER WHERE USER_ID LIKE '%@central-domain%'; #check existing users that belong to central-domain
UPDATE SBI_USER SET USER_ID = REPLACE(USER_ID,'@central-domain','@groupnet') WHERE USER_ID LIKE '%@central-domain%';
select * from SBI_USER WHERE USER_ID LIKE '%@central-domain%'; #check that no user left to central-domain
```
> Ndef: Before moving all users at once to the new domain you can first test just one. For example:
UPDATE SBI_USER SET USER_ID = REPLACE(USER_ID,'@groupnet.gr','@groupnet') WHERE USER_ID LIKE '%enomikos@groupnet.gr%'
select * from SBI_USER WHERE USER_ID LIKE '%enomikos@groupnet.gr%'