# Manage IDM Replication

## Description
This procedure outlines the steps required to manage and troubleshoot replication between two FreeIPA (IDM) nodes. The replication is performed on the LDAP service using GSSAPI authentication (Kerberos) via `ldap/_HOST` Service Principal Names (SPNs). The setup ensures high availability and keeps both Key Distribution Centers (KDCs) synchronized.

## Prerequisites
- Access to `idm1.bigdata.abc.gr` and `idm2.bigdata.abc.gr` with administrative privileges.
- Valid Kerberos ticket for executing `ipa` and `kadmin` commands.
- Knowledge of FreeIPA replication mechanisms.

## Affected Systems / Scope
- **IDM (FreeIPA) Nodes:** `idm1.bigdata.abc.gr`, `idm2.bigdata.abc.gr`
- **Kerberos Service Principals:** `ldap/idm1.bigdata.abc.gr`, `ldap/idm2.bigdata.abc.gr`
- **Cloudera Services Authentication**
- **Preauthentication for Service Principals**

## Procedure Steps

### **1. Check Replication Status**
1. **Authenticate with Kerberos**
   ```bash
   kinit <admin user>
   ```
2. **List Replication Targets**
   ```bash
   ipa-replica-manage list -v
   ```
3. **Verify Replication from Another Node**
   ```bash
   ipa-replica-manage list -v idm2.bigdata.abc.gr
   ```
   - Expected output:
     ```
     idm1.bigdata.abc.gr: replica
       last update status: Error (0) Replica acquired successfully: Incremental update succeeded
       last update ended: 2023-12-21 12:41:17+00:00
     ```

---

### **2. Force Replication**
1. **Authenticate with Kerberos**
   ```bash
   kinit <admin user>
   ```
2. **Initiate Force Sync**
   ```bash
   ipa-replica-manage force-sync --from idm2.bigdata.abc.gr
   ```
   - Expected output:
     ```
     ipa: INFO: Setting agreement cn=meToidm1.bigdata.abc.gr,cn=replica,cn=dc\=bigdata\,dc\=abc\,dc\=gr,cn=mapping tree,cn=config schedule to 2358-2359 0 to force sync
     ipa: INFO: Replication Update in progress: FALSE: status: Error (0) Replica acquired successfully: Incremental update succeeded
     ```

---

## Actions Taken / Expected Output
- Verified that IDM replication is working correctly.
- Forced synchronization to resolve any replication delays.
- Identified potential issues with preauthentication settings.

## Notes and Warnings
> If replication issues persist, check `krbTicketFlags` for inconsistencies.  
> Ensure Kerberos preauthentication is correctly configured to avoid `NO_PREAUTH` errors.

---

## Troubleshooting / Error Handling

### **1. Issue: Preauthentication Problems**
#### **Description**
- When Cloudera Services failed over from `CNE.abc.GR` to `BIGDATA.abc.GR`, users from `CNE.abc.GR` could not authenticate.
- To fix this, preauthentication was disabled for SPNs:
  ```bash
  ipa config-mod --ipaconfigstring="KDC:Disable Default Preauth for SPNs"
  ```

#### **Problems Created**
1. **`krbtgt/BIGDATA.abc.GR` requires preauthentication, while SPNs do not.**
   - Running `kinit -R` fails with `NO_PREAUTH`, impacting the Hue Kerberos Renewer.
   - Workaround: Hue's Kerberos ticket cache is renewed via `cron`.

2. **Replication from `idm2.bigdata.abc.gr` to `idm1.bigdata.abc.gr` failed (`NO_PREAUTH`).**
   - The service principal `ldap/idm2.bigdata.abc.gr` was rejected by `idm1.bigdata.abc.gr`.

---

### **2. Investigate Service Principals**
#### **Check Service Principal Details**
1. **On `idm1.bigdata.abc.gr`**
   ```bash
   ipa service-find ldap/idm1.bigdata.abc.gr --all --raw
   ```
   - Expected output includes:
     ```
     krbTicketFlags: 128
     ```

2. **On `idm2.bigdata.abc.gr`**
   ```bash
   ipa service-find ldap/idm2.bigdata.abc.gr --all --raw
   ```
   - Expected output:
     ```
     krbTicketFlags: 0
     ```

#### **Check via `kadmin`**
1. **On `idm1.bigdata.abc.gr`**
   ```bash
   kadmin.local -q "get_principal ldap/idm1.bigdata.abc.gr"
   ```
   - Expected output:
     ```
     Attributes: REQUIRES_PRE_AUTH
     ```

2. **On `idm2.bigdata.abc.gr`**
   ```bash
   kadmin.local -q "get_principal ldap/idm2.bigdata.abc.gr"
   ```
   - Expected output:
     ```
     Attributes:
     ```

---

### **3. Fix Preauthentication Issue**
1. **Remove Preauthentication Requirement**
   ```bash
   kadmin.local -q "modify_principal -requires_preauth ldap/idm1.bigdata.abc.gr"
   ```
   - This change is replicated to `idm2`.

2. **Re-enable Preauthentication When `CNE.abc.GR` is Removed**
   ```bash
   kadmin.local -q "modify_principal +requires_preauth ldap/idm1.bigdata.abc.gr"
   ipa config-mod --ipaconfigstring=""
   ipactl restart
   ```

---

## References
