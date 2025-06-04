---
title: Enable Spark and YARN ACLs for Log Access
description: Step-by-step guide to configure ACLs in Spark and YARN for allowing specific groups access to Spark logs and MapReduce job logs in Cloudera Manager.
tags:
  - spark
  - yarn
  - acl
  - logs
  - cloudera
  - permissions
  - jobhistory
  - spark-ui
  - sysadmin
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  services:
    - Spark
    - YARN
  cloudera_components:
    - Spark History Server
    - JobHistory Server
  acl_groups:
    - WBDADMIN
    - WBDOPDEV
    - WBDOPPRO
    - WBDOPQA
---
# Enable ACLs in Spark and YARN for Log Access
This procedure describes how to enable ACLs (Access Control Lists) in YARN and Spark using Cloudera Manager. This configuration is necessary to allow specific user groups to access Spark logs and MapReduce job logs.
## Step 1: Configure YARN ACLs
### a. Edit ACL Settings for Job Viewing
1. Go to **Cloudera Manager > YARN > Configuration**.
2. Search for **"ACL for viewing a job"**.
3. Add the required groups that should have access to view MapReduce job logs.  
Example value:
hue WBDADMIN,WBDOPDEV,WBDOPPRO,WBDOPQA
> **Be careful with the syntax.** Click the question mark icon in Cloudera Manager for exact formatting rules.
### b. Enable Default Group ACLs for JobHistory Server
1. Still under YARN > Configuration, search for:
- **Enable Job ACLs**
- **JobHistory Server Default Group**
2. Enable the option and ensure the appropriate groups are assigned if needed.
## Step 2: Configure Spark ACLs
1. Go to **Cloudera Manager > Spark > Configuration**.
2. Search for **Spark Client Advanced Configuration Snippet (Safety Valve) for spark-conf/spark-defaults.conf**.
3. Add the following lines to enable ACLs and define group access:
```properties
spark.acls.enable=true
spark.admin.acls.groups=WBDADMIN
spark.history.ui.admin.acls.groups=WBDADMIN
spark.ui.view.acls.groups=WBDOPDEV,WBDOPPRO,WBDOPQA
```
These settings control who can view Spark UI logs and access Spark History Server in the cluster.