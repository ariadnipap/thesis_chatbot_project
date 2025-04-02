# Manage HBase Quotas

## Enable HBase quotas
1. Go to ```Cloudera Manager => HBase => Configuration => HBase Service Advanced configuration Snippet (Safety Valve) for hbase-site.xml```
2. Add the following configuration:
   ```
   Name: hbase.quota.enabled
   Value: true
   Description: enable hbase quotas
   ```
3. Restart HBase service

## Add HBase quotas to a namespace

1. ssh to an edge node
2. kinit as hbase
   ```bash
   cd /var/run/cloudera-scm-agent/processes
   ls –ltr HBASE
   cd <latest hbase process folder>
   kinit -kt hbase.keytab `hostname`
   ```
3. Get list of namespaces
   ```bash
   hbase shell
   list_namespace
   ```
4. Set throttle READ quotas 
   ```bash
   hbase shell
   set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => ‘namespace', LIMIT => 'Xreq/sec'
   ```
5. Set throttle WRITE quotas
   ```bash
   hbase shell
   set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => ‘namespace', LIMIT => 'Xreq/sec'
   ```
6. Show all quotas
   ```bash
   hbase shell
   list_quotas
   ```
## Remove HBase quotas from a namespace

1. ssh to an edge node
2. kinit as hbase
   ```bash
   cd /var/run/cloudera-scm-agent/processes
   ls –ltr HBASE
   cd <latest hbase process folder>
   kinit -kt hbase.keytab `hostname`
   ```
3. Get list of namespaces and list of quotas already set
   ```bash
   hbase shell
   list_namespace
   list_quotas
   ```
4. Delete throttle quotas
   ```bash
   hbase shell
   set_quota TYPE => THROTTLE, NAMESPACE => ‘namespace', LIMIT => NONE
   ```
5. Verify that quotas have been removed
   ```bash
   hbase shell
   list_quotas
   ```