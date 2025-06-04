---
title: Add New Yum Repository on Nexus
description: Procedure for creating a new YUM (proxy) repository in Nexus, configuring repository metadata, and registering the repo on edge nodes using a custom `.repo` file.
tags:
  - nexus
  - yum
  - proxy-repo
  - edge-nodes
  - firefox
  - repository-management
  - sysadmin
  - bigstreamer
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  tools:
    - Nexus Repository Manager
    - YUM
    - Firefox
  nodes:
    - xedge0x
    - edge nodes
  nexus_url: https://999.999.999.999:8081/
  internal_links:
    - https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/passwords.kdbx
---
# Below procedure describes how to add a new repository on Nexus.
This guide explains how to add and register a new YUM (proxy) repository using Nexus Repository Manager and configure it on BigStreamer edge nodes.
## Prerequisites
- Access to an edge node with GUI (X11 forwarding)
- Nexus credentials from [passwords.kdbx](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/passwords.kdbx)
## Open Nexus Web Interface
1. Login with your personal account to an edge node and open firefox
Start Firefox with GUI support from an edge node:
```bash
ssh -X xedge0x
firefox
```
## Create Yum Proxy Repository
2. When firefox window pops up login to `https://999.999.999.999:8081/` with Nexus creds.
[Click me for the credentials](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/passwords.kdbx)
## Add Repository to Edge Node
3. Click on the gear icon and then **repositories** button and **Create repository** and select **yum (proxy)**.
Add below values:
- **Name**: name_of_repo
- **Remdef storage**: remdef_storage_url 
- **Maximum Component age**: 20
- **Minimum Component age**: 20
- **Clean up policies**: daily_proxy_clean
Leave the rest of the settings as default
4. Click on **Create repository**
## Verify Repository Access
5. Login with your personal account at node and add the following repos:
Create the new YUM repository definition file:
```bash
vi /etc/yum.repos.d/name_of_repo.repo
[name_of_repo]
name = name_of_repo
baseurl = http://999.999.999.999:8081/repository/name_of_repo.repo
enabled = 1
gpgcheck = 0
```
6. Check and add new repo
Clean cache, check for updates, and verify repo registration:
```bash
ssh to_node
yum clean all
yum check-update > /tmp/test-repo.txt
yum repolist
```