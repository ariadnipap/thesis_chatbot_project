---
title: SSL Configuration Hardening for Edge Nodes
description: Procedure for updating SSL configurations for httpd, nginx, haproxy, and sshd on PR and DR edge nodes to enforce TLSv1.2, disable weak ciphers, and enhance cryptographic security.
tags:
  - ssl
  - tls
  - httpd
  - nginx
  - haproxy
  - sshd
  - tls1.2
  - edge-nodes
  - security-hardening
  - bigstreamer
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  nodes:
    - pr1edge01
    - pr1edge02
    - dr1edge01
    - dr1edge02
  services:
    - httpd
    - nginx
    - haproxy
    - sshd
  ssl_protocol: TLSv1.2
  backup_paths:
    - /etc/httpd/conf.d/ssl.conf
    - /etc/httpd/conf/httpd.conf
    - /etc/httpd/conf.d/graphite-web.conf
    - /etc/nginx/nginx.conf
    - /etc/haproxy/haproxy.cfg
    - /etc/ssh/sshd_config
---
# SSL Hardening Procedure for Edge Services
All procedures pertain to PR and DR edge nodes:
- pr1edge01
- pr1edge02
- dr1edge01
- dr1edge02
## Preparation
Before continuing with the changes it is best to put the edge node you are
working on in standby mode, so as to not disrupt services:
```bash
$ ssh Exxxx@XXXedgeXX
$ sudo -i
```
And follow the procedures described in the **Switchover of Cluster Resources** chapter
of the **Security Vulnerabilities** MOP [here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx).
## Step 1: Harden Apache httpd SSL Configuration
Enforce TLSv1.2 and disable weak ciphers in Apache httpd.
Backup the old httpd configs:
```bash
# cp -ap /etc/httpd/conf.d/ssl.conf  "/etc/httpd/conf.d/ssl.conf.bak.$(date +%Y%m%d)"
# cp -ap /etc/httpd/conf/httpd.conf  "/etc/httpd/conf/httpd.conf.bak.$(date +%Y%m%d)"
# cp -ap /etc/httpd/conf.d/graphite-web.conf "/etc/httpd/conf.d/graphite-web.conf.bak.$(date +%Y%m%d)"
```
Add the following line in `/etc/httpd/conf/httpd.conf`:
```
TraceEnable Off
```
Add the following line in `/etc/httpd/conf/httpd.conf`, `/etc/httpd/conf.d/ssl.conf`
and `/etc/httpd/conf.d/graphite-web.conf`:
```
SSLProtocol +TLSv1.2
```
Edit `/etc/httpd/conf/httpd.conf`, `/etc/httpd/conf/ssl.conf` and
`/etc/httpd/conf/graphite-web.conf` and remove the following lines:
```
SSLHonorCipherOrder Off
SSLCipherSuite ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES256:ECDH+AES128:!aNULL:!SHA1:!AESCCM:!MD5:!3DES:!DES:!IDEA
```
Restart the **httpd** service:
```bash
# systemctl restart httpd
```
## Step 2: Harden nginx SSL Configuration
Harden nginx SSL config by restricting protocols.
Backup the old **nginx.conf**:
```bash
# cp -ap /etc/nginx/nginx.conf "/etc/nginx/nginx.conf.bak.$(date +%Y%m%d)"
```
Add the following line in `/etc/nginx/nginx.conf`:
```
ssl_protocols TLSv1.2;
```
Disable and restart the **nginx** service:
```bash
# systemctl disable --now nginx
# systemctl start nginx
```
## Step 3: Update haproxy SSL Bindings
Add TLSv1.2 bindings and update HAProxy certificate paths.
Backup the old **haproxy.cfg**:
```bash
# cp -ap /etc/haproxy/haproxy.cfg "/etc/haproxy/haproxy.cfg.bak.$(date +%Y%m%d)"
```
Add options for 8889 and 25002 port and repeat for **hue_vip**:
```
bind 999.999.999.999:25002 ssl crt no-sslv3 /opt/haproxy/security/x509/node.haproxy.pem
```
Restart the **haproxy** service:
```bash
# systemctl restart haproxy
```
## Step 4: Strengthen SSH Daemon Cryptographic Settings
Strengthen SSH security by configuring allowed ciphers and key exchanges.
Backup the old **sshd_config**:
```bash
# cp -ap /etc/ssh/sshd_config "/etc/ssh/sshd_config.bak.$(date +%Y%m%d)"
```
Edit the sshd config `/etc/ssh/sshd_config` and add the following:
```
Ciphers aes256-ctr,aes192-ctr,aes128-ctr # 5.2.11
KexAlgorithms ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha256
```
Restart the **sshd** service:
```bash
# systemctl restart sshd
```