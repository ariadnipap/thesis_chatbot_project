---
title: Grafana Upgrade Procedure for PR/DR Edge Nodes
description: Step-by-step procedure to upgrade Grafana OSS on PR and DR edge nodes in BigStreamer, including plugin and dashboard backup, RPM repository setup, execution using YUM, and rollback instructions.
tags:
  - grafana
  - monitoring
  - upgrade
  - rollback
  - dashboards
  - plugins
  - bigstreamer
  - rpm
  - yum
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  systems:
    - pr1edge01
    - pr1edge02
    - dr1edge01
    - dr1edge02
    - pr1node01
  components:
    - grafana
    - grafana-server
    - grafana.ini
    - datasources
    - dashboards
  backup_targets:
    - /var/lib/grafana/plugins
    - /etc/grafana/grafana.ini
    - API backups of dashboards/datasources
  rpm_repository_host: pr1node01
---
# Grafana Upgrade
All procedures pertain to PR and DR edge nodes, except the RPM repository creation
which is performed on pr1node1:
- pr1edge01
- pr1edge02
- dr1edge01
- dr1edge02
## Pre-Upgrade Preparation and Backups
This section includes backing up Grafana plugins, INI configuration, dashboards, and datasources, and preparing RPM repositories for PR/DR edge nodes.
Before continuing with the changes it is best to inform the monitoring team
that there will be an outage on the monitoring service.
Login to each edge node and get a root shell:
```bash
$ ssh Exxxx@XXXedgeXX
$ sudo -i
```
### Backup
Backup Installed plugins before you upgrade them in case you want to rollback the
Grafana version and want to get the exact same versions you were running before the
upgrade or in case you add new configuration options after upgrade and then rollback.
- pr1edge01:
  - Plugins: `# tar -zcvf grafana_plugins_edge01.tar.gz /var/lib/grafana/plugins`
  - INI file: `# tar -zcvf grafana_ini_edge01.tar.gz /etc/grafana/grafana.ini`
Backup Grafana Datasources and Dashboards
With an admin account login to Grafana and go to Configuration > API keys. Create a new key by clicking on “Add API key” with role admin. Copy the authorization token for the key.
Login to an edge node and use the API to back up the datasources and dashboards:
```bash
# curl -H "Authorization: Bearer <insert token>"  https://<grafana host>:3000/api/datasources > grafana_datasources.json
# curl -H "Authorization: Bearer <insert token>"  https://<grafana host>:3000/api/search | grep -o -E '"uid":"[a-zA-Z0-9_-]+"' | sed 's/"uid":"//g' | sed 's/"//g' > grafana_dashboards_uids
# for uid in `cat grafana_dashboards_uids`; do curl -H "Authorization: Bearer <insert token>"  https://<grafana host>:3000/api/dashboards/uid/${uid}; done > /tmp/grafana_dashboard_${uid}.json
```
### Repositories
Download Grafana RPMs from [Grafana Downloads](https://grafana.com/grafana/download?edition=oss)
and prepare their repositories on pr1node01, from where PR and DR edge nodes will download them:
```bash
$ ssh Exxxx@pr1node01
$ sudo -i
# mkdir -p /var/www/grafana8/Packages/
```
Move all the downloaded RPMs under `/var/www/html/grafana8/Packages` and create the
repository:
```bash
# cd /var/www/grafana8
# createrepo .
```
If the repository already exists, issue:
```bash    
# createrepo --update .
```
Login to an edge node, create the repository file and copy it to all other
edge nodes appropriately:
```bash
$ ssh Exxx@XXXedgeXX
$ sudo -i
# vi /etc/yum.repos.d/grafana8.repo
[grafana8]
name = Grafana8
baseurl =  http://pr1node01.mno.gr/grafana8/
enabled = 1
gpgcheck = 0
# scp /etc/yum.repos.d/grafana8.repo repo XXXedgeXX:/etc/yum.repos.d/
```
## Upgrade Execution on All Edge Nodes
This section explains how to stop Grafana, perform the YUM upgrade, and verify the updated Grafana server and configuration.
Login to each edge node, stop the **grafana-server**, and update it using **YUM**:
```bash
$ ssh Exxx@XXXedgeXX
$ sudo -i
# systemctl stop grafana-server
# systemctl status grafana-server
# yum clean all
# yum update grafana
# systemctl start grafana-server
# systemctl  status grafana-server
```
Check Grafana UI, Dashboards and compare new and old configs with **diff** for any discrepancies:
```bash
# sdiff /etc/grafana/grafana.ini <path/to/old/grafana.ini>`
```
## Rollback Grafana to Previous Version
This section covers how to revert Grafana to the previous version, restore configuration and plugins, and verify dashboard functionality.
Login to each edge node to stop the grafana service and downgrade the package using **YUM**:
```bash
$ ssh Exxx@XXXedgeXX
$ sudo -i
# systemctl stop grafana-server
# systemctl status grafana-server
# yum clean all
# yum downgrade grafana
```
Restore plugins and INI files from the backups previously created at `grafana_plugins_edge0X.tar.gz`
and `grafana_ini_edge0X.tar.gz`, start the grafana service and check dashboards:
```bash
# systemctl start grafana-server
# systemctl status grafana-server
```