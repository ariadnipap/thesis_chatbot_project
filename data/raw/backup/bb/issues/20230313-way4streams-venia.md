# mno - BigStreamer - way4streams-venia - Kerberos Authentication Errors on new Way4Streams installation

<b>Description:</b>

```text
Reporting and investigation for this issue was performed in a teams call, since we did not have access to the server that Way4Streams was installed.

The error we were facing was something along the lines

/way4/DEVUSER.keytab does not contain any keys for DEVUSER@BANK.CENTRAL.mno.GR
```

<b>Actions Taken:</b>

1. The new server hosting the application is RHEL 8 instead of Solaris. We tried to manually `kinit`

From the server with `way4`

``` bash
kinit DEVUSER@BANK.CENTRAL.mno.GR -kt /way4/DEVUSER.keytab
```

Output:

```bash
Ticket cache: KCM:1500
Default principal: DEVUSER@BANK.CENTRAL.mno.GR

Valid starting       Expires              Service principal
15/03/2023 12:35:29  16/03/2023 12:35:29  krbtgt/BANK.CENTRAL.mno.GR@BANK.CENTRAL.mno.GR
	renew until 22/03/2023 12:35:29
```

2. **Anything** but `FILE` ticket caches is sure to create a problem.

From the server with `root`:

``` bash
vi /etc/krb5.conf
```

Change the following under `libdefaults` section:

``` conf
default_ccache_name = FILE:/tmp/krb5cc_%{uid}
```

Also, remove `sssd-kcm`

```bash
yum remove sssd-kcm
```

3. After that the klist output used a `FILE` cache, but the problem persisted.

Since the OS problems were resolved we focused the keytab.

From the server with `way4`

``` bash
klist -kte /way4/DEVUSER.keytab
```

Output:

```
Keytab name: FILE:/way4/DEVUSER.keytab
KVNO Timestamp           Principal
---- ------------------- ------------------------------------------------------
  0 01/01/1970 00:00:00 DEVUSER@BANK.CENTRAL.mno.GR (DEPRECATED:arc4-hmac) 
```

That DEPRECATED flag is not a good sign. 

4. Searching for `rc4-hmac` and `OpenJDK11` we stumbled upon this link https://bugs.openjdk.org/browse/JDK-8262273

From the server with `root`:

``` bash
vi /etc/krb5.conf
```

Add the following under `libdefaults` section:

``` conf
allow_weak_crypto = true
```

The issue was resolved!

<b>Affected Systems:</b>

Way4Streams QA (Not supported by jkl)

<b>Action Points:</b>
