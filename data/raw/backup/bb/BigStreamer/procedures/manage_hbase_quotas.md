# Manage HBase Quotas

## Description
This document outlines the procedure for managing HBase quotas, including enabling quotas, adding quotas to namespaces, and removing quotas.

## Prerequisites
- Access to **Cloudera Manager** for enabling quotas.
- SSH access to an **edge node**.
- Proper Kerberos authentication (`kinit`) as the HBase user.
- Knowledge of existing HBase namespaces.

## Procedure Steps

### 1. Enable HBase Quotas
1. Navigate to **Cloudera Manager**:
   ```
   Cloudera Manager => HBase => Configuration => HBase Service Advanced configuration Snippet (Safety Valve) for hbase-site.xml
   ```
2. Add the following configuration:
   ```
   Name: hbase.quota.enabled
   Value: true
   Description: Enable HBase quotas
   ```
3. Restart the **HBase service**.

---

### 2. Add HBase Quotas to a Namespace

#### a. SSH to an edge node:
```bash
ssh <user>@<edge-node>
```

#### b. Authenticate as HBase user:
```bash
cd /var/run/cloudera-scm-agent/processes
ls -ltr HBASE
cd <latest hbase process folder>
kinit -kt hbase.keytab `hostname`
```

#### c. Get the list of namespaces:
```bash
hbase shell
list_namespace
```

#### d. Set throttle **READ** quotas:
```bash
hbase shell
set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => 'namespace', LIMIT => 'Xreq/sec'
```

#### e. Set throttle **WRITE** quotas:
```bash
hbase shell
set_quota TYPE => THROTTLE, THROTTLE_TYPE => WRITE, NAMESPACE => 'namespace', LIMIT => 'Xreq/sec'
```

#### f. Verify quotas:
```bash
hbase shell
list_quotas
```

---

### 3. Remove HBase Quotas from a Namespace

#### a. SSH to an edge node:
```bash
ssh <user>@<edge-node>
```

#### b. Authenticate as HBase user:
```bash
cd /var/run/cloudera-scm-agent/processes
ls -ltr HBASE
cd <latest hbase process folder>
kinit -kt hbase.keytab `hostname`
```

#### c. Get the list of namespaces and quotas:
```bash
hbase shell
list_namespace
list_quotas
```

#### d. Delete quotas:
```bash
hbase shell
set_quota TYPE => THROTTLE, NAMESPACE => 'namespace', LIMIT => NONE
```

#### e. Verify quotas have been removed:
```bash
hbase shell
list_quotas
```

---

## Actions Taken / Expected Output
- HBase quotas are successfully **enabled**, **configured**, or **removed**.
- Verification of quotas using `list_quotas`.

## Notes and Warnings
> - Ensure you have the correct **namespace name** before setting quotas.
> - Incorrect quota limits can impact **performance**.
> - Restarting the HBase service after enabling quotas may cause **temporary downtime**.

## Affected Systems / Scope
- **HBase clusters** managed via Cloudera.
- **Namespaces** where quotas are applied.

## Troubleshooting / Error Handling

### Common Issues:
- **Issue:** Unable to list namespaces.  
  **Solution:** Ensure that you have authenticated using `kinit`.

- **Issue:** Quotas not applying.  
  **Solution:** Verify that `hbase.quota.enabled` is set to `true` and restart the HBase service.

- **Issue:** Performance degradation after applying quotas.  
  **Solution:** Check if the quota limits are set too low.

### Log File Locations:
```bash
# Check HBase logs for quota-related issues
tail -f /var/log/hbase/*.log
```

## References
- [Cloudera Documentation](https://www.cloudera.com/)

