# Manage Wildfly

## Description
Integration between the **Big Data clusters** and the **backend servers** of mno is done over **REST APIs**. The applications that handle the **HTTP calls** are installed on the edge servers of both sites. **At normal operation, only one site is active.** These applications are deployed on **Wildfly instances**.

There are four sets of Wildfly installations:
- **Internet Banking (`ibank`)**
- **Online (`online`)**
- **Two other application sets developed by mno**

All application servers are managed by **supervisord**, owned by the **root user**.

---

## Prerequisites
- Administrator privileges for accessing Wildfly instances.
- SSH access to the **edge servers**.
- Access to **supervisord** for managing Wildfly processes.
- Knowledge of the **load balancer configurations**.
- Awareness of the **production and development environment paths**.

---

## Scope

### **Glossary**
- **NetScaler**: Loadbalancer managed by mno, handling **SSL offloading**.
- **VIP**: Virtual IP of the **Loadbalancer**.
- **SNIP**: IP of the **Loadbalancer** that initiates connections to Wildfly instances.
- **Health Check**: Endpoint used by the Loadbalancer to determine if a **Wildfly instance is active**, expecting a `HTTP 200/OK` response.

---

## Setup

### **Internet Banking Wildfly Instances**

#### **prodrestib**
- **Handles:** Ingestion and queries for the Internet Banking (`ibank`) flow.
- **User:** `PRODREST`
- **Port:** `8080`
- **Health Check Endpoint:** `/trlogibank/app`
- **Supervisor Configuration:** `/etc/supervisor.d/wildfly-prodrestib.ini`
- **Installation Path:** `/opt/wildfly/default/prodrestib`
- **Deployments Path:** `/opt/wildfly/default/prodrestib/standalone/deployments`
- **General Configuration Path:** `/opt/wildfly/default/prodrestib/standalone/configuration/standalone.xml`
- **Application Configuration Path:** `/opt/wildfly/default/prodrestib/standalone/configuration/BigStreamer/beanconfig/translogApiIBankJmxConfig.xml`
- **Application Logs:** `/var/log/wildfly/prodrestib/server.log`
- **Access Log:** `/var/log/wildfly/prodrestib/access.log`

#### **prodrestibmetrics**
- **Hosts applications developed by mno** and accessed by Internet Banking backend servers.
- **Not supported** by jkl Telecom S.A.
- **User:** `PRODREST`
- **Port:** `8081`
- **Health Check Endpoint:** `/ibankmetrics/app`
- **Supervisor Configuration:** `/etc/supervisor.d/wildfly-prodrestibmetrics.ini`
- **Installation Path:** `/opt/wildfly/default/prodrestibmetrics`
- **Deployments Path:** `/opt/wildfly/default/prodrestibmetrics/standalone/deployments`
- **General Configuration Path:** `/opt/wildfly/default/prodrestibmetrics/standalone/configuration/standalone.xml`
- **Application Configuration Path:** `Managed by mno`
- **Application Logs:** `/var/log/wildfly/prodrestibmetrics/server.log`
- **Access Log:** `/var/log/wildfly/prodrestibmetrics/access.log`

---

### **Internet Banking Loadbalancer Farms**
There are **two active Loadbalancers** for Internet Banking. 
1. **Original setup:** Routes all traffic to `prodrestib`.
2. **Routing setup:** Routes conditionally between `prodrestib` and `prodrestibmetrics`.

---

### **Online Wildfly Instances**

#### **prodreston**
- **Handles:** Ingestion and queries for the **Online (`online`) flow**.
- **User:** `PRODREST`
- **Port:** `8080`
- **Health Check Endpoint:** `/trlogonline/app`
- **Supervisor Configuration:** `/etc/supervisor.d/wildfly-prodreston.ini`
- **Installation Path:** `/opt/wildfly/default/prodreston`
- **Deployments Path:** `/opt/wildfly/default/prodreston/standalone/deployments`
- **General Configuration Path:** `/opt/wildfly/default/prodreston/standalone/configuration/standalone.xml`
- **Application Configuration Path:** `/opt/wildfly/default/prodreston/standalone/configuration/BigStreamer/beanconfig/translogApiOnlineJmxConfig.xml`
- **Application Logs:** `/var/log/wildfly/prodreston/server.log`
- **Access Log:** `/var/log/wildfly/prodreston/access.log`

#### **prodrestintapps**
- **Hosts applications developed by mno** and accessed by the Online backend servers.
- **Not supported** by jkl Telecom S.A.
- **User:** `PRODREST`
- **Port:** `8081`
- **Health Check Endpoint:** `/intapps/app`
- **Supervisor Configuration:** `/etc/supervisor.d/wildfly-prodrestintapps.ini`
- **Installation Path:** `/opt/wildfly/default/prodrestintapps`
- **Deployments Path:** `/opt/wildfly/default/prodrestintapps/standalone/deployments`
- **General Configuration Path:** `/opt/wildfly/default/prodrestintapps/standalone/configuration/standalone.xml`
- **Application Configuration Path:** `Managed by mno`
- **Application Logs:** `/var/log/wildfly/prodrestintapps/server.log`
- **Access Log:** `/var/log/wildfly/prodrestintapps/access.log`

---

## Procedure Steps

### **Stopping a Wildfly Instance (`prodrestib` or `prodreston`)**
#### a. Shutdown Health Check Endpoint:
```bash
curl -XPUT https://<hostname>:8080/trlogibank/app/app-disable
```

#### b. Stop Wildfly Instance:
```bash
supervisorctl stop wildfly-prodrestib
```
or
```bash
supervisorctl stop wildfly-prodreston
```

#### c. Verify that the instance is down:
```bash
ps -ef | grep 'prodrestib/'
supervisorctl status wildfly-prodrestib
tail -f /var/log/wildfly/prodrestib/server.log
tail -f /var/log/wildfly/prodrestib/access.log
```

---

### **Starting a Wildfly Instance (`prodrestib` or `prodreston`)**
#### a. Start Wildfly Instance:
```bash
supervisorctl start wildfly-prodrestib
```
or
```bash
supervisorctl start wildfly-prodreston
```

#### b. Verify that the instance is running:
```bash
ps -ef | grep 'prodrestib/'
supervisorctl status wildfly-prodrestib
tail -f /var/log/wildfly/prodrestib/server.log
tail -f /var/log/wildfly/prodrestib/access.log
```

---

## Actions Taken / Expected Output
- **Wildfly instances** successfully started or stopped.
- **Loadbalancers update their configurations** automatically.
- **No HTTP errors** in logs after instance restart.

---

## Notes and Warnings
> - Do not manually modify Loadbalancer configurations **without confirmation from mno**.
> - Ensure that all configuration paths **match production values** before restarting instances.

---

## Affected Systems / Scope
- **Internet Banking (`ibank`) Wildfly Instances**
- **Online (`online`) Wildfly Instances**
- **Loadbalancer Farms** for traffic routing.

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Wildfly does not restart** → Check configuration files for errors.
- **Loadbalancer does not recognize the instance** → Ensure health check endpoint returns `HTTP 200/OK`.
- **High response time after restart** → Check server logs for startup delays.

### **Log File Locations**
```bash
tail -f /var/log/wildfly/prodrestib/server.log
tail -f /var/log/wildfly/prodreston/server.log
tail -f /var/log/wildfly/prodrestib/access.log
tail -f /var/log/wildfly/prodreston/access.log
```

---

## References
- [Cloudera Documentation](https://www.cloudera.com/)

