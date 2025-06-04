---
title: InfiniBand Card Replacement Procedure
description: Step-by-step procedure for safely replacing an InfiniBand (IB) card in a BigStreamer cluster node, including pre-checks, interface cleanup, and recommissioning in Cloudera Manager.
tags:
  - infiniband
  - ib
  - hardware-replacement
  - cloudera
  - maintenance
  - hca
  - smpartition
  - arp
  - kudu
  - recommission
  - network
  - node-replacement
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  services:
    - Cloudera Manager
    - Kudu
  nodes:
    - bda01node05
    - bda01sw-ib1
  network_interfaces:
    - bondeth1
    - bondeth2
  monitoring_tools:
    - sminfo
    - ibnetdiscover
    - smpartition
    - ip
    - arp
    - ksck
  reference:
    - MOS Doc ID 1985159.1
---
# InfiniBand HCA Card Replacement Procedure
Replacing an IB card require powering off the host. Before doing so some checks must be performed and the host must be decommissioned. After replacing, some configurations must be performed in the interfaces and the roles recommissioned.
This document outlines the required steps for replacing a failed InfiniBand HCA (Host Channel Adapter) card on a BigStreamer cluster node. It covers node decommissioning from Cloudera Manager, checking for non-default IB partitions, post-replacement interface configuration cleanup, and recommissioning of the node and roles. It also links to the relevant Oracle MOS document in case IB partitions need manual GUID replacement. Use this guide whenever you are performing planned maintenance involving InfiniBand hardware replacement.
## Step 1: Decommission the Host
To decommission the node from Cloudera Manger, select the specific host and:
1. Enter maintenance mode
2. Select decommission roles
3. If a datanode role is present on this host, take it offline for at least 4 hours
## Step 2: Check for Non-Default IB Partitions
Most probably only the default IB partitions are present. To check this perform the following steps provided
by Oracle:
```
Ndef:
If a system uses custom non-default InfiniBand partitions [e.g., Exalogic (virtual/physical/hybrid), Exadata (virtual/physical), SuperCluster, BDA] then the HCA Port GUIDs might need to be updated in the InfiniBand partition(s) after replacing an HCA.Determine the switch running as Primary. From it, check for any custom, non-default IP partitions.
[root@bda01node05 ~]# sminfo
sminfo: sm lid 15 sm guid 0x10e0406d5aa0a0, activity count 26263191 priority 14 state 3 SMINFO_MASTER
[root@bda01node05 ~]# ibnetdiscover | grep 10e0406d5aa0a0
switchguid=0x10e0406d5aa0a0(10e0406d5aa0a0)
Switch 36 "S-0010e0406d5aa0a0" # "SUN DCS 36P QDR bdax01sw-ib1 xxx.xxx.171.24" enhanced port 0 lid 15 lmc 0
[root@bda01node05 ~]# ssh root@xxx.xxx.171.24
[root@bda01sw-ib1 ~]# smpartition list active
# Sun DCS IB partition config file
# This file is generated, do not edit
#! version_number : 0
Default=0x7fff, ipoib : ALL_CAS=full, ALL_SWITCHES=full, SELF=full;
SUN_DCS=0x0001, ipoib : ALL_SWITCHES=full;
If there are IB partitions other than default partitions, then refer to MOS ndef 1985159.1 for additional steps that will need to be taken before the old HCA is removed.
```
- [MOS ndef 1985159.1](https://support.oracle.com/epmos/faces/DocumentDisplay?parent=SrDetailText&sourceId=3-37179888534&id=1985159.1)
If `smpartition list active` shows output similar to the above, no actions are needed. If not the attached procedure must followed in order to replace the UUIDs.
## Step 3: Fix Network Interface ARP Config
Oracle runs an automated configuration scripts that sets arp checking of the gateway in certain interfaces. If
the interfaces are non-routable, as is the case for bondeth1 and bondeth2, these options must be removed.
1. Check for any interfaces that should not be in the DOWN state with `ip a`
2. ssh into another known with known good configs
3. compare the interfaces in question with the interfaces in the changed hosts and remove any option not present in the known-good node. Generally these would be options referring to ARP.
4. Bring the interfaces down with `ifdown <IFCACE_NAME>`
5. Bring it back up with `ifup <IFCACE_NAME>`
6. Check if the interfaces are in the UP state with `ip a`
7. Check that ARP entries are complete with `arp`
## Step 4: Recommission the Node in Cloudera Manager
Recommission the node through cloudera manager. Recommissioning and starting roles in the same step might fail so it is best to recommission first without starting roles.
1. Recommission without starting roles
2. Start roles
After everything is back online the kudu tablet on the host might not have taken on any tablets. This
is normal as all tablets have been replicated to the other hosts. With time it will take on tablets as
well.
This can be verified using `ksck` as the kudu user.