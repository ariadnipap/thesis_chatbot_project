# How to change Openldap Manager password

For every ldasearch the password of `Manager` is [here](KnowledgeBase/prodsyspasswd.kdbx)

1. Login into kerb1 node as root:

```bash
ssh kerb1
sudo -i
```

2. Use command-line in order to create a  slapd password

```bash
slappasswd -h {SSHA}
```

3. Store the output which will be start like `{SSHA}xxxxxxx` 

4. Create ldif files change password

a.

```bash
vi changepwconfig.ldif

dn: olcDatabase={0}config,cn=config
changetype: modify
replace: olcRootPW
olcRootPW: paste the output from step `3`
```
b.

```bash
vi changepwmanager.ldif

dn: olcDatabase={2}bdb,cn=config
changetype: modify
replace: olcRootPW
olcRootPW: paste the output from step `3`
```

5. Backup `config` and `data` of openldap:

```bash
slapcat -n 0 -l config.ldif
slapcat -n 2 -l data.ldif
```

6. Modify Manager password:
```bash
ldapmodify -H ldapi:// -Y EXTERNAL -f changepwmanager.ldif
ldapmodify -H ldapi:// -Y EXTERNAL -f changepwconfig.ldif
```

7. Checks 

a. Via command line

For `kerb1`. Where `uid` add a ldap user. e.g your ldap username:

```bash
ldapsearch -H ldaps://kerb1.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"  'uid=xxxx'
```

For `kerb2`. Where `uid` add a ldap user. e.g your ldap username::

```bash
ldapsearch -H ldaps://kerb2.bigdata.abc.gr -D "cn=Manager,dc=bigdata,dc=abc,dc=gr" -W -b "ou=People,dc=bigdata,dc=abc,dc=gr"  'uid=xxxx'
```

b. Via `UI`.

Login into `admin` node as `root`:

Open firefox
```bash
firefox
```
phpldapadmin link: https://kerb1.bigdata.abc.gr/phpldapadmin/

Try to connect with the new `Manager` password
