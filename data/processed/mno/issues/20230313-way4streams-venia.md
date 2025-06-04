---
title: Kerberos Authentication Errors on Way4Streams (RHEL 8) Due to Keytab and Ticket Cache Issues
description: A Kerberos authentication issue occurred on a new Way4Streams installation (RHEL 8) due to invalid ticket cache type and deprecated key encryption (arc4-hmac); resolved by updating krb5.conf and enabling weak crypto support.
tags:

* mno
* bigstreamer
* kerberos
* keytab
* kinit
* klist
* arc4-hmac
* openjdk
* rhel8
* krb5.conf
* allow\_weak\_crypto
* ticket cache
* kcm
* file-based ticket cache
* way4streams
* authentication failure
* deprecated encryption
* sssd-kcm
* java kerberos
* teams call
* way4
  last\_updated: 2025-05-01
  author: ilpap
  context:
  issue\_id: way4streams-venia
  system: Way4Streams QA (non-jkl supported)
  root\_cause: Keytab used deprecated arc4-hmac encryption and RHEL 8 defaulted to KCM ticket cache, which is incompatible
  resolution\_summary: Forced use of FILE ticket cache, removed sssd-kcm, and enabled weak crypto in krb5.conf to support legacy keytab
  operating\_system: RHEL 8
  java\_version: OpenJDK 11
  kerberos\_principal: [DEVUSER@BANK.CENTRAL.mno.GR](mailto:DEVUSER@BANK.CENTRAL.mno.GR)
---
# mno - BigStreamer - way4streams-venia - Kerberos Authentication Errors on new Way4Streams installation
## Description
Kerberos authentication failed during setup of Way4Streams on a new RHEL 8 server. The main issue was that the provided keytab used deprecated `arc4-hmac` encryption, and the OS defaulted to using an incompatible KCM ticket cache. This blocked application authentication with error messages indicating missing keys. The problem was resolved by forcing a file-based ticket cache, removing the `sssd-kcm` service, and enabling support for weak crypto in `/etc/krb5.conf`.
```
/way4/DEVUSER.keytab does not contain any keys for DEVUSER@BANK.CENTRAL.mno.GR
```
## Actions Taken
1. The new server hosting the application is RHEL 8 instead of Solaris. We tried to manually `kinit`
From the server with `way4`:
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
Also, remove `sssd-kcm`:
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
After enabling weak crypto and restarting authentication, `kinit` and application login worked correctly. The Kerberos authentication problem was resolved.
## Affected Systems
Way4Streams QA (Not supported by jkl)
## Troubleshooting Keywords
arc4-hmac, deprecated keytab, OpenJDK 11, Kerberos ticket cache, RHEL 8, authentication error, weak crypto, DEVUSER, krb5.conf, KCM, sssd-kcm, kinit fails, way4streams