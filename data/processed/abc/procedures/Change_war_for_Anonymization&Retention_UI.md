---
title: "Permanent Anonymization & Retention UI Access Issue and WAR Replacement"
description: "Troubleshooting and resolution steps for the abc BigStreamer Permanent Anonymization & Retention UI access issue due to CDN resource blocking over VPN. Involves replacing the Wildfly WAR deployment."
tags:
  - abc
  - bigstreamer
  - wildfly
  - anonymization
  - retention
  - ui issue
  - vpn restriction
  - deployment
  - war replacement
  - haproxy
  - trustcenter
---
# abc - Permanent Anonymization & Retention UI issue
This guide documents the root cause and resolution steps for the abc Permanent Anonymization & Retention UI failing to load over VPN due to external CDN dependency, and the WAR file replacement procedure on Wildfly.
## Description
```
Regarding the problem with the Permanent Anonymization & Retention UI (https://cne.def.gr:8643/customapps)
Let me remind you that access to this particular UI is not possible via VPN.
The reason is that it is trying to load a library from the internet (cdn.jsdelivr.net).
A new war has been added which should replace the old one in wildfly.
```
## Actions Taken
## Actions Taken

1. SSH into `unc2` using your personal account.
2. Switch to root and check HAProxy backend configuration:
   sudo -i
   less /etc/haproxy/haproxy.cfg
   (Search for the `tru-backend` section.)
3. Connect to `unekl1` and back up the existing WAR file:
   ssh unekl1
   cp -rp /opt/trustcenter/wf_cdef_trc/standalone/deployments/wftrust-landing-web.war /opt/trustcenter/wf_cdef_trc/standalone/deployments/wftrust-landing-web.war.bkp
4. Set correct permissions on the new WAR file:
   chown trustuser:trustcenter <new_war_file>
   chmod 644 <new_war_file>
5. Move the new WAR file to the deployments directory:
   mv <new_war_file> /opt/trustcenter/wf_cdef_trc/standalone/deployments/
6. No Wildfly restart is required. A .deployed marker file (wftrust-landing-web.war.deployed) will be created automatically.
7. Verify Wildfly is running:
   su - trustuser
   bash
   trust-status
8. Repeat steps 3–7 on `unekl2`.
9. Clear your browser cache and access the UI at:
   https://cne.def.gr:8643/customapps
## Affected Systems
abc Bigstreamer