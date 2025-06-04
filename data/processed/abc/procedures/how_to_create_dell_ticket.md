---
title: "abc - BigStreamer - How to Open a Ticket to DELL"
description: "Step-by-step instructions for opening a hardware support ticket with DELL for abc BigStreamer nodes, including gathering the service tag and exporting TSR logs from iDRAC."
tags:
  - dell support
  - hardware ticket
  - tsr logs
  - idrac
  - ipmitool
  - bigstreamer
  - abc
  - service tag
  - vnc
  - server diagnostics
  - supportassist
---
This document describes how to open a hardware support ticket to DELL for an abc BigStreamer node, including instructions to retrieve the node's iDRAC IP, collect TSR logs via iDRAC, and deliver them to DELL support.
# abc - BigStreamer - How to open a ticket to DELL
## Description
Below is a step-by-step description of the process from opening a ticket to collecting TSR logs from iDRAC.
## Actions Taken
1. ssh with your personal account on the issue node.
2. Switch to root and find the iDRAC management IP:
```bash
sudo -i
ipmitool lan print | grep -i 'IP Address'
# If ipmitool is missing:
yum install ipmitool
```
3. Open Firefox on a VNC session and navigate to the iDRAC IP address found in Step 2.
4. From `Server-->Overview-->Server Information` copy the `Service Tag number`
5. Call Dell support `2108129800`. They need the `Service Tag number` from step 4
6. A DELL engineer will create a case and send you all the necessary instructions. If not the link to collect the TSR logs is `https://www.dell.com/support/kbdoc/el-gr/000126803/export-a-supportassist-collection-via-idrac7-and-idrac8`
7. Inform `abc` before any action on the IDRAC.
8. Download the TSR `.zip` file locally from the iDRAC interface. If using VNC on a node like `un4`, the downloaded files will be stored under: `/home/cloudera/Downloads/`. The filename format is: `TSR<date>_<service_tag>.zip`.
9. Send the zip file/files to DELL and wait for their response.
## Completion
You have now completed the process. Await DELL’s response and proceed based on their instructions.