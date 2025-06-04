---
title: "Nagios Alarms & Errors - Fork, SSH, Return Code 255"
description: "Steps to resolve common Nagios issues on BigStreamer admin nodes including 'fork: retry', 'ssh_exchange_identification: Connection closed', and 'Return code 255 is out of bounds' by adjusting ulimits, SSH command options, and Nagios configuration settings."
tags:
  - nagios
  - bigstreamer
  - monitoring
  - fork error
  - ssh_exchange_identification
  - return code 255
  - max_concurrent_checks
  - bashrc
  - nagios.cfg
  - commands.cfg
  - ssh
  - alerts
  - admin
  - abc
---
# Nagios Alarms & Errors
**Component**: Nagios  
**Environment**: BigStreamer  
**Owner**: kpar  
**Status**: Closed  
**Date**: 2021-05-12  
**Issue Number**: -  
## Description
This document describes how to resolve the following Nagios errors:
- `/etc/bashrc: fork: retry: Resource temporarily unavailable`
- `ssh_exchange_identification: Connection closed by remote host`
- `Return code of 255 is out of bounds`
## Resolution Steps
### 1. Fix "fork: retry" Error
As root or as the `nagios` user, edit the `.bashrc` file:
```bash
vi /home/nagios/.bashrc
```
Add the following lines:
```bash
ulimit -u 8888
ulimit -n 2222
```
---
### 2. Fix SSH "Connection closed by remote host" Error
As root, edit the following Nagios command file:
```bash
vi /usr/local/nagios/etc/objects/commands.cfg
```
Replace this line:
```bash
$USER1$/check_by_ssh  -H $HOSTADDRESS$ -t 30 -C "/usr/lib/nagios/plugins/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$"
```
With this:
```bash
$USER1$/check_by_ssh -E 8 -o StrictHostKeyChecking=no -H $HOSTADDRESS$ -t 30 -C "/usr/lib/nagios/plugins/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$"
```
---
### 3. Fix "Return code of 255 is out of bounds" Error
As root, edit the Nagios configuration file:
```bash
vi /usr/local/nagios/etc/nagios.cfg
```
Find and change the following setting:
```bash
max_concurrent_checks=50
```
Then restart the Nagios service:

```bash
service nagios restart
```
---
## Keywords
logs, fork, bounds, connection closed, ssh, ulimit, max_concurrent_checks, Nagios admin