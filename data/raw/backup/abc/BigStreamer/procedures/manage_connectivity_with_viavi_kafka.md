# Manage Connectivity with Viavi Kafka

## Description
This procedure outlines the steps required to configure and manage connectivity between Viavi’s Kafka cluster and BigStreamer’s datanodes. The objective is to replace the existing SFTP-based feed for RAN.AI Geolocation with a Spark Streaming application utilizing Kafka.

## Prerequisites
- Access to `incelligent` node with root privileges.
- HAProxy installed and configured.
- DNS entries set up for Kafka brokers.
- Network connectivity to VLAN 300.
- Administrative access to IDM for managing DNS entries.

## Affected Systems / Scope
- **Viavi Kafka Cluster**
- **BigStreamer Datanodes**
- **HAProxy Configuration on Incelligent Node**
- **DNS Configuration for Internal Cluster Communication**

## Procedure Steps

### **1. Setup and Configuration**

- The Kafka cluster is secured using internal users and TLS encryption.
- Three new IPs (VLAN 300) have been added to the `incelligent` node.
- Hostnames of Kafka brokers are mapped to internal IPs via DNS.

#### **HAProxy Configuration**
- The HAProxy configuration enables TCP-based load balancing between BigStreamer’s network and Viavi’s Kafka brokers.
- Below is the configuration used in `/etc/haproxy/haproxy.cfg`:

  ```conf
  global
      log         999.999.999.999 local2
      chroot      /var/lib/haproxy
      pidfile     /var/run/haproxy.pid
      maxconn     4000
      user        haproxy
      group       haproxy
      daemon
      stats socket /var/lib/haproxy/stats

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

---

### **2. Manage HAProxy**
#### **Start HAProxy**
- Run the following command from the `incelligent` node:
  ```bash
  systemctl start haproxy
  ```

#### **Stop HAProxy**
- To stop the service:
  ```bash
  systemctl stop haproxy
  ```

#### **Check HAProxy Status**
- Verify that HAProxy is running and listening on the correct ports:
  ```bash
  systemctl status haproxy
  ss -tulnp | grep 9093  # Check listening port
  ```

#### **Check Connectivity to HAProxy**
- Use `nc` (netcat) to verify connectivity:
  ```bash
  nc -zv 999.999.999.999 9093  # Check HAProxy IP 1
  nc -zv 999.999.999.999 9093  # Check HAProxy IP 2
  nc -zv 999.999.999.999 9093  # Check HAProxy IP 3
  ```

#### **Check Connectivity to Kafka Brokers**
- Ensure Kafka brokers are reachable:
  ```bash
  nc -zv 999.999.999.999 9093  # Check broker 1
  nc -zv 999.999.999.999 9093  # Check broker 2
  nc -zv 999.999.999.999 9093  # Check broker 3
  ```

---

### **3. Manage DNS Entries**
- Login to the IDM portal to modify DNS settings:
  ```
  https://admin.bigdata.abc.gr/ipa/ui/
  ```
- Update internal DNS records to map Kafka broker hostnames to the new VLAN 300 IPs.

---

## Actions Taken / Expected Output
- **Network connectivity:** BigStreamer’s datanodes can reach Viavi’s Kafka cluster.
- **HAProxy Configuration:** TCP-based forwarding is set up and active.
- **DNS Resolution:** Internal hostnames correctly resolve to their assigned IPs.

## Notes and Warnings
> Using a single node for connectivity ensures that network traffic does not overwhelm BigStreamer’s uplinks.  
> Always verify DNS entries and HAProxy logs before troubleshooting network issues.

## Troubleshooting / Error Handling
- **If HAProxy does not start:**
  ```bash
  journalctl -xe -u haproxy
  ```
- **If Kafka clients fail to connect:**
  ```bash
  tail -f /var/log/haproxy.log
  ```
- **If DNS resolution fails:**
  ```bash
  nslookup geolightgr35.geo.abc.gr
  ```

## References
- [IDM Admin Panel](https://admin.bigdata.abc.gr/ipa/ui/)

