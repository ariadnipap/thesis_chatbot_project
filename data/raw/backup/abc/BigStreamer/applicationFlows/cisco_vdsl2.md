# PIRAEUS CISCO VDSL2

## 1. Overview

`Piraeus Cisco Vdsl2 App` is an application that polls data every 5 minutes using SNMP, transforms the SNMP output files, merges them into a single file, and then transfers the data to an SFTP server and an HDFS directory for customer retrieval. The application runs inside a Kubernetes pod.

**Key Information**
- **Pod User:** `root`
- **Pod Scheduler:** `Cron`
- **Kubernetes Namespace:** `piraeus-cisco-vdsl2-deployment`
- **Cluster User:** `ipvpn`
- **Container Registry:** `kubemaster-vip.bigdata.abc.gr/piraeus-cisco-vdsl2-app`
- **Execution Schedule:** `Every 5 minutes`
- **Pod Script:** `/app/run_vdsl2.sh`
- **Main Configuration File:** `/app/conf/application.yaml`
- **Hadoop Table:** `bigcust.vdsl2`
- **Logs:** Use `kubectl logs` to view `stdout`

## 2. Installation & Configuration

### 2.1. Useful Links
- [Piraeus Cisco VDSL2 App](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-app)
- [Piraeus Cisco VDSL2 DevOps](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-devops)
- [Piraeus Cisco VDSL2 Deployment](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-deployment)
- [Wiki Page](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-devops/-/wikis/home)
- [File Definitions](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-devops/-/wikis/File-Definitions)
- [Monitoring](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/home)
- [Deployment Instructions](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-deployment/-/blob/main/Readme.md)

## 3. Data Processing

### 3.1. SNMP Polling of Elements
The application polls data using SNMP. The raw files produced contain component metrics ([4 metrics](#5-metrics) for each element) of the network elements and are stored locally inside a Kubernetes pod.

**Configuration**
- **Output Path:** `/app/conf/application.yaml` → `snmppoller.dataDir`
- **Output File Name Pattern:** `nnmcp.vdsl-g*.\*.txt`
- **Elements Configuration:** `/app/conf/application.yaml` → `snmppoller.endpoints`
- **Keystore Path:** `/app/conf/application.yaml` → `snmppoller.keyStoreFilePath`

### 3.2. Transformation of SNMP Files
After the data has been polled, the application transforms the output files into CSV format while structuring the data appropriately.

**Configuration**
- **Output Path:** `/app/conf/application.yaml` → `vdsl2.dataDir`
- **Output File Name Pattern:** `/app/conf/application.yaml` → `vdsl2.filePattern`
- **Input File Pattern:** `nnmcp.vdsl-g*.\*.txt.csv`

### 3.3. Merging of Transformed Files
The application merges all CSV files with the same timestamp into a single deliverable file.

**Configuration**
- **Output Path:** `/app/conf/application.yaml` → `fmerger.dataDir`
- **Output File Name Pattern:** `/app/conf/application.yaml` → `fmerger.filePattern`
- **Input File Pattern:** `VDSL2_*.csv`

### 3.4. SFTP Transfer
The application transfers the merged file to an SFTP server.

**Configuration**
- **Source Path:** `/app/conf/application.yaml` → `ssh.source`
- **Destination Path:** `/app/conf/application.yaml` → `ssh.remdef`
- **SFTP Host:** `/app/conf/application.yaml` → `ssh.host`
- **SFTP User:** `/app/conf/application.yaml` → `ssh.user`
- **SFTP Key:** `/app/conf/application.yaml` → `ssh.prkey`

### 3.5. HDFS Transfer
The application transfers the merged file to an HDFS directory for archiving.

**Configuration**
- **Source Path:** `/app/conf/application.yaml` → `hdfsput.dataDir`
- **HDFS URL:** `/app/conf/application.yaml` → `hdfsput.hdfsURL`
- **Destination Path:** `/app/conf/application.yaml` → `hdfsput.hdfsPath`
- **Hadoop User:** `/app/conf/application.yaml` → `hdfsput.hadoopUser`
- **Hadoop Site:** `/app/conf/application.yaml` → `hdfsput.hadoopSite`
- **Kerberos Configuration:** `/app/conf/application.yaml` → `hdfsput.kerberos.krb5conf`
- **Kerberos Keytab Path:** `/app/conf/application.yaml` → `hdfsput.kerberos.keytab`
- **Kerberos Principal:** `/app/conf/application.yaml` → `hdfsput.kerberos.principal`

## 4. Monitoring & Debugging

### 4.1. Logs
Logs are stored in `stdout` and can be accessed using:


