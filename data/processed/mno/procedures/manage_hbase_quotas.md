---
title: Manage HBase Quotas on BigStreamer
description: Procedure for enabling, setting, and removing HBase namespace-level read and write quotas in a Cloudera-managed environment on BigStreamer using Cloudera Manager and HBase shell.
tags:
  - hbase
  - quotas
  - cloudera
  - throttling
  - hbase-shell
  - namespace
  - read-quota
  - write-quota
  - bigstreamer
  - cm-safety-valve
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  components:
    - HBase
    - Cloudera Manager
  systems:
    - edge nodes
  commands:
    - hbase shell
    - kinit
    - Cloudera Safety Valve
---
# Manage HBase Quotas
This document describes how to manage HBase quotas in the BigStreamer environment. It explains how to enable HBase throttling via Cloudera Manager, configure namespace-specific read and write request limits using the HBase shell, and cleanly remove quotas when no longer needed. Steps include using kinit, navigating HBase processes, and verifying changes through list_quotas.
## Step 1: Enable Global HBase Quotas via Cloudera Manager
1. Go to ```Cloudera Manager => HBase => Configuration => HBase Service Advanced configuration Snippet (Safety Valve) for hbase-site.xml```
2. Add the following configuration:
```
Name: hbase.quota.enabled
Value: true
Description: enable hbase quotas
```
3. Restart HBase service
## Step 2: Set Namespace-Level HBase Quotas
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
set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => 'namespace', LIMIT => 'Xreq/sec'
```
5. Set throttle WRITE quotas
```bash
hbase shell
set_quota TYPE => THROTTLE, THROTTLE_TYPE => READ, NAMESPACE => 'namespace', LIMIT => 'Xreq/sec'
```
6. Show all quotas
```bash
hbase shell
list_quotas
```
## Step 3: Remove Namespace-Level Quotas
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
set_quota TYPE => THROTTLE, NAMESPACE => 'namespace', LIMIT => NONE
```
5. Verify that quotas have been removed
```bash
hbase shell
list_quotas
```