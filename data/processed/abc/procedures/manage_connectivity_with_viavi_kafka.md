---
title: "Manage Connectivity with Viavi Kafka"
description: "Configuration and operational steps for setting up HAProxy, DNS, and connectivity between BigStreamer and Viavi's Kafka cluster using a single node (Incelligent) with TCP passthrough and TLS encryption."
tags:
  - viavi
  - kafka
  - haproxy
  - vlan300
  - tls
  - tcp
  - kafka-proxy
  - kafka-client
  - vpn
  - dns
  - incelligent
  - bigstreamer
  - vlan
  - geolocation
  - spark-streaming
  - devops
  - network
  - connectivity
  - procedure
  - admin
---
This document describes the configuration of secure connectivity between BigStreamer and Viavi's Kafka brokers via HAProxy using internal VLAN 300. It includes HAProxy setup, DNS configuration, and procedures for managing services and validating access.
# Viavi Kafka Integration via HAProxy
- [Manage Connectivity with Viavi Kafka](#manage-connectivity-with-viavi-kafka)
  - [Setup](#setup)
    - [HAProxy Configuration](#haproxy-configuration)
  - [Procedure](#procedure)
    - [Manage HAProxy](#manage-haproxy)
    - [Manage DNS entries](#manage-dns-entries)
## Setup
Incelligent wants to develop an application with Viavi's Kafka cluster as the datasource.This project aims to replace the current feed that powers RAN.AI Geolocation that is based on SFTP file transfers with a Spark Streaming application. Kafka Cluster is secured using internal/local users and TLS encryption.
abc requested to expose Viavi's Kafka Cluster to BigStreamer's datanodes and enable the development of the application.
In order to achieve the connectivity we have added three new IPs (VLAN 300) to the Incelligent node and we have assigned the hostnames from the Kafka Brokers to these internal IPs with DNS entries on the cluster's internal DNS.
The reason we have used only one node for the connectivity is that the traffic from this flow can possibly saturate all uplinks of the BigStreamer which would impact other flows.
``` mermaid
graph TD
  subgraph internal [Internal BigStreamer Network - VLAN 300]
  A[Kafka Client]
  A-->A1
  A-->B1
  A-->C1
  subgraph proxy [incelligent node]
    A1[999.999.999.999:9093<br>geolightgr35.geo.abc.gr - Intenral DNS]
    B1[999.999.999.999:9093<br>geolightgr36.geo.abc.gr - Intenral DNS]
    C1[999.999.999.999:9093<br>geolightgr37.geo.abc.gr - Intenral DNS]
  end 
  end
  subgraph kafka [Viavi's Kafka]
    A2[999.999.999.999:9093<br>geolightgr35.geo.abc.gr - Actual Broker]
    B2[999.999.999.999:9093<br>geolightgr36.geo.abc.gr - Actual Broker]
    C2[999.999.999.999:9093<br>geolightgr37.geo.abc.gr - Actual Broker]
  end
  A1-->|HAProxy - Mode TCP|A2
  B1-->|HAProxy - Mode TCP|B2
  C1-->|HAProxy - Mode TCP|C2
```
### HAProxy Configuration
```conf
global
    # to have these messages end up in /var/log/haproxy.log you will
    # need to:
    #
    # 1) configure syslog to accept network log events.  This is done
    #    by adding the '-r' option to the SYSLOGD_OPTIONS in
    #    /etc/sysconfig/syslog
    #
    # 2) configure local2 events to go to the /var/log/haproxy.log
    #   file. A line like the following can be added to
    #   /etc/sysconfig/syslog
    #
    #    local2.*                       /var/log/haproxy.log
    #
    log         999.999.999.999 local2

    chroot      /var/lib/haproxy
    pidfile     /var/run/haproxy.pid
    maxconn     4000
    user        haproxy
    group       haproxy
    daemon

    # turn on stats unix socket
    stats socket /var/lib/haproxy/stats

#---------------------------------------------------------------------
# common defaults that all the 'listen' and 'backend' sections will
# use if not designated in their block
#---------------------------------------------------------------------
defaults
    mode                    http
    log                     global
    option                  httplog
    option                  dontlognull
    option http-server-close
    option forwardfor       except 999.999.999.999/8
    option                  redispatch
    retries                 3
    timeout http-request    10s
    timeout queue           1m
    timeout connect         10s
    timeout client          1m
    timeout server          1m
    timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 3000

listen viavi-megafeed-kafka1

   bind 999.999.999.999:9092
   mode tcp
   balance leastconn

   server viavi-megafeed-kafka1 999.999.999.999:9092

listen viavi-megafeed-kafka2

   bind 999.999.999.999:9092
   mode tcp
   balance leastconn

   server viavi-megafeed-kafka2 999.999.999.999:9092

listen viavi-megafeed-kafka3

   bind 999.999.999.999:9092
   mode tcp
   balance leastconn

   server viavi-megafeed-kafka3 999.999.999.999:9092

listen viavi-megafeed-kafka1_ssl

   bind 999.999.999.999:9093
   mode tcp
   balance leastconn

   server viavi-megafeed-kafka1 999.999.999.999:9093

listen viavi-megafeed-kafka2_ssl

   bind 999.999.999.999:9093
   mode tcp
   balance leastconn

   server viavi-megafeed-kafka2 999.999.999.999:9093

listen viavi-megafeed-kafka3_ssl

   bind 999.999.999.999:9093
   mode tcp
   balance leastconn

   server viavi-megafeed-kafka3 999.999.999.999:9093
```
## Procedure
### Manage HAProxy
Start - From incelligent node as root
``` bash
systemctl start haproxy
```
Stop - From incelligent node as root
``` bash
systemctl stop haproxy
```
Check - From incelligent node as root
``` bash
systemctl status haproxy
ss -tulnp | grep 9093 # Check listening port
nc -zv 999.999.999.999 9093 # Check HAProxy IP 1
nc -zv 999.999.999.999 9093 # Check HAProxy IP 2
nc -zv 999.999.999.999 9093 # Check HAProxy IP 3
nc -zv 999.999.999.999 9093 # Check broker 1
nc -zv 999.999.999.999 9093 # Check broker 2
nc -zv 999.999.999.999 9093 # Check broker 3
```
### Manage DNS entries
Login to [IDM](https://admin.bigdata.abc.gr/ipa/ui/) with an administrative account to manage DNS entries