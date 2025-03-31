# abc - [One Domain] RCPE integration with GROUPNET

<b>Description:</b>

```
This document describes the procedure of changing current domain from `central-domain.root.def.gr` to `groupnet` along with their users

Servers:

999.999.999.999 PVDCAHR01.groupnet.gr
999.999.999.999 PVDCLAM01.groupnet.gr

Useful info:

PROD
- rcpe1.bigdata.abc.gr, rcpe2.bigdata.abc.gr, 
- https://999.999.999.999:8843/rcpe/#/login
- https://999.999.999.999:8843/rcpe/#/login
- https://cne.def.gr:8843/rcpe/#/login

TEST
- unc2.bigdata.abc.gr
- https://999.999.999.999:8743/rcpe/
```

> Ndef: Following procedure occurs for test. Be sure to apply the same steps for prod 



### Prerequisites

1. Check if the ssl certificates of the groupnet have already been imported

```bash
[root@unc2 ~]# openssl s_client -connect PVDCAHR01.groupnet.gr:636
[root@unc2 ~]# openssl s_client -connect PVDCLAM01.groupnet.gr:636
```

If they are not been imported, you should import them using formual at `admin:etc/salt/salt/tls/certificate_authority/import_ca.sls`.

2. Customer should send an active user that belongs to the new domain for testing 
3. `/etc/hosts` file must be updated to all  BigStreamer servers with the new domain 
4. Perfom an ldap search for the given user:
```
ldapsearch -H ldaps://PVDCAHR01.groupnet.gr -W -b "dc=groupnet,dc=gr" -D "<Bind User sAMAccountName>" '(sAMAccountName=...)'
```

### New Domain Creation

1. Login to https://999.999.999.999:8743/rcpe/ with the credentilas you have
2. On the main screen select **User Management** on the left of the page
3. Select **Domain** from the tabs on the left
4. Select **Create New** button at the bottom of the view.
5. Enter the name and description of the new domain (DOMAINS_NAME: groupnet.gr, DOMAINS_DESCRIPTION: GROUPNET Domain)
6. Select **Create** button at the bottom of the view.


### Create users for the new domain

> Ndef: This section should be only followed in case the given user does not belong to RCPE. You can check that from **Users** Tab and seach for the username. 
1. Select **Users** from the tabs on the left.
2. Select **Create New** button at the bottom of the view to create a new user
3. Enter the username and the required information for the newly user given by the customer ( Domain Attribute included ). 
> Ndef: You should not add a password here
5. Select **Create** button at the bottom of the view.
6. Click on **Fetch All** to view existing users including the new one
7. Click on the **magnifying glass** button next to the name of the newly created user in order to assign roles and click on button **USERS_ASSIGN_ROLES** , add SSO-Administrator and click on **Submit**.

**Time to update sso-configuration**

1. Login to `test_r_cpe` user

```bash
ssh unc2
su - test_r_cpe #r_cpe for prod
```

2. Check trcpe status
```bash
[test_r_cpe@unc2 ~]$ trcpe-status #rcpe-status for prod
```

3. Stop trcpe
```bash
[test_r_cpe@unc2 ~]$ trcpe-stop #rcpe-stop for prod
```

4. Back up sso configuration for central

```bash
[test_r_cpe@unc2 ~]$ cp /opt/test_r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security.xml /opt/test_r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security-backup.xml
#/opt/r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security.xml path for prod 
```

5. Move newly sso conf file from `/home/users/ilpap/sso-security-groupnet.xml` to the below path:

`[test_r_cpe@unc2 ~]$ mv /home/users/ilpap/sso-security-groupnet.xml /opt/test_r_cpe/standalone/configuration/ServiceWeaver/sso/sso-security.xml`

6. Start trcpe and check status
```bash
trcpe-start
trcpe-status
```
7. Login to https://999.999.999.999:8743/rcpe/ with user and shared credentials. You must be able to see the newly created domain.


### Move users to the created domain

1. Back up mysql SSO_USERS table:
```bash
mysqldump -u root  -p test_r_cpe SSO_USERS --single-transaction > /tmp/SSO_USERS_BACKUP.sql
```

2. Move all users that have domain `central-domain.root.def.gr` to `groupnet.gr`
```bash
[root@db01 ~]# mysql -u root -p;
mysql> use test_r_cpe;
mysql> show tables;
mysql> select * FROM SSO_DOMAINS LIMIT 5; #newly domain_ID is 5
mysql> show create table SSO_USERS; #Domain_ID is currently 3
mysql> UPDATE SSO_USERS SET DOMAIN_ID=5 WHERE DOMAIN_ID=3;
mysql> select * FROM SSO_USERS where DOMAIN_ID=5;
```


### Domain Deletion


1. Login with a user authorized with SSO access rights on the application

2. On the main screen select User Management on the left of the page

3. Select Domain from the tabs on the left

4. Select the domain you want to delete by clicking on the left of the record

5. Select Delete Row(s) button at the bottom of the view.

6. Verify deletion  ( select Yes, delete on the pop-up view )


**Congrats!**
