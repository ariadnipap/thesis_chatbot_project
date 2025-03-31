# PIRAEUS CISCO VDSL2

## Useful links

- [Piraeus Cisco VDSL2 App](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-app)
- [Piraeus Cisco VDSL2 DevOps](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-devops)
- [Piraeus Cisco VDSL2 Deployment](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-deployment)
- [Wiki Page](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-devops/-/wikis/home)
- [File Definitions](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-devops/-/wikis/File-Definitions)
- [Monitoring](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/home)
- [Deployment Instructions](https://metis.ghi.com/obss/bigdata/abc/ipvpn/piraeus-cisco-vdsl2/piraeus-cisco-vdsl2-deployment/-/blob/main/Readme.md)

## Overview

`Piraeus Cisco Vdsl2 App` is an application that polls data every 5 minutes using SNMP, transforms the SNMPs output files, concatenates the files to one output file and then places it to an SFTP server and an HDFS directory, in order to be retrieved by the customer. The application runs in a Kubernetes pod. [Monitoring App](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/home#prod) is used for monitoring and health checks.

**Pod User:** `root`  
**Pod Scheduler:** `Cron`  
**Kubernetes Namespace** `piraeus-cisco-vdsl2-deployment`  
**Cluster User** `ipvpn`  
**Container Registry** `kubemaster-vip.bigdata.abc.gr/piraeus-cisco-vdsl2-app`  
**Schedule:** `Every 5 minutes`  
**Pod Script:** `/app/run_vdsl2.sh`  
**Main Configuration File:** `/app/conf/application.yaml`  
**Logs:** Use `kubectl logs` to view `stdout`  
**Hadoop Table:** `bigcust.vdsl2`

## Application Components

### SNMP Polling of Elements

``` mermaid
  graph TD
  A[Piraeus Bank VTUs] -->|SNMP Polling| B[File: nnmcp.vdsl-g*.\*.txt <br> Path: /app/work/data <br> Pod ]
```

The application polls data using SNMP. The raw files produced, contain component metrics ([4 metrics](#metrics) for each Element) of the network elements and are stored in local path inside a Kubernetes pod.

**Output Path Configuration:** `/app/conf/application.yaml` -> `snmppoller.dataDir`  
**Output File Name Pattern:** `nnmcp.vdsl-g*.\*.txt`  
**Elements Configuration File:** `/app/conf/application.yaml` -> `snmppoller.endpoints`  
**Keystore Path Configuration:** `/app/conf/application.yaml` ->  `snmppoller.keyStoreFilePath`

### Transformation of SNMP files

``` mermaid
  graph TD
  B[File: nnmcp.vdsl-g*.\*.txt <br> Path: /app/work/data <br> Pod ] --> |Transform|D[File: nnmcp.vdsl-g*.\*.txt.csv <br> Path: /app/work/data <br> Pod ]
```

After the data has been polled, the application transforms the output files to respective CSV files while formatting the data to fit the desired formation. The files are stored in local path inside a Kubernetes pod.

**Output Path Configuration:** `/app/conf/application.yaml` -> `vdsl2.dataDir`  
**Output File Name Pattern Configuration:** `/app/conf/application.yaml` -> `vdsl2.filePattern`  
**Input File Pattern:** `nnmcp.vdsl-g*.\*.txt.csv`  

### Merging of transformed files

``` mermaid
  graph TD
  D[File: nnmcp.vdsl-g*.\*.txt.csv <br> Path: /app/work/data <br> Pod ] --> |Merge|E[File: VDSL2_*.csv <br> Path: /app/work/data <br> Pod ]
```

The application then merges all the output csv files, which have the same timestamp, and produce a single deliverable file.

**Output Path Configuration:** `/app/conf/application.yaml` -> `fmerger.dataDir`  
**Output File Name Pattern Configuration:** `/app/conf/application.yaml` -> `fmerger.filePattern`  
**Input File Pattern:** `VDSL2_*.csv`  

### SFTP Transfer

``` mermaid
  graph TD
  E[File: VDSL2_*.csv <br> Path: /app/work/data <br> Pod ] --> |SFTP|F[File: VDSL2_*.csv <br> Path:/shared/abc/ip_vpn/out/vdsl2 <br> Host: un-vip.bigdata.abc.gr/999.999.999.999]
```

The Piraeus Cisco Vdsl2 App places the deliverable file in an sftp server.

**Input Step Configuration:** `/app/conf/application.yaml` -> `ssh.inputFrom`
**Input File Source Path Configuration:** `/app/conf/application.yaml` -> `ssh.source`  
**SFTP Destination Path Configuration:** `/app/conf/application.yaml` -> `ssh.remdef`  
**SFTP Host Configuration:** `/app/conf/application.yaml` -> `ssh.host`  
**SFTP User Configuration:** `/app/conf/application.yaml` -> `ssh.user`  
**SFTP Key Configuration:** `/app/conf/application.yaml` -> `ssh.prkey`  
  
### HDFS transfer

``` mermaid
  graph TD
  E[File: VDSL2_*.csv <br> Path: /app/work/data <br> Pod ] --> |HDFS|G[File: VDSL2_*.csv <br> Path:/ez/warehouse/bigcust.db/landing_zone/ext_tables/piraeus_vdsl2 <br> HDFS]
```

The Piraeus Cisco Vdsl2 App places the deliverable file in a hdfs directory for archiving.

**Input Step Configuration:** `/app/conf/application.yaml` -> `hdfsput.inputFrom` //From which step it gets the files to put to hdfs  
**Input File Path Configuration:** `/app/conf/application.yaml` -> `hdfsput.dataDir`  
**Output HDFS URL Configuration:** `/app/conf/application.yaml` -> `hdfsput.hdfsURL`  
**Output HDFS Destination Path Configuration:** `/app/conf/application.yaml` -> `hdfsput.hdfsPath`  
**Hadoop User Configuration:** `/app/conf/application.yaml` -> `hdfsput.hadoopUser`  
**Hadoop Site Configuration:** `/app/conf/application.yaml` -> `hdfsput.hadoopSite`  
**Kerberos Configuration File:** `/app/conf/application.yaml` -> `hdfsput.kerberos.krb5conf`  
**Kerberos User Keytab Path Configuration:** `/app/conf/application.yaml` -> `hdfsput.kerberos.keytab`  
**Kerberos Principal Configuration:** `/app/conf/application.yaml` -> `hdfsput.kerberos.principal`

## Metrics

| Requirement                         | Metric                          | Metric OID                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------------------------------- | ------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Connected (actual) Speed downstream | xdsl2LineStatusAttainableRateDs | transmission.999.999.999.999.1.20 | Maximum Attainable Data Rate Downstream. The maximum downstream net data rate currently attainable by the xTU-C transmitter and the xTU-R receiver, coded in bit/s.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Connected (actual) Speed upstream   | xdsl2LineStatusAttainableRateUs | transmission.999.999.999.999.1.21 | Maximum Attainable Data Rate Upstream. The maximum upstream net data rate currently attainable by the xTU-R transmitter and the xTU-C receiver, coded in bit/s.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Signal Attenuation per band         | xdsl2LineBandStatusSigAtten     | transmission.999.999.999.999.1.3  | When referring to a band in the downstream direction, it is the measured difference in the total power transmitted by the xTU-C and the total power received by the xTU-R over all  subcarriers of that band during Showtime. When referring to a band in the upstream direction, it is the measured difference in the total power transmitted by the xTU-R and the total power received by the xTU-C over all subcarriers of that band during Showtime. Values range from 0 to 1270 in units of 0.1 dB (physical values are 0 to 127 dB). A special value of 0x7FFFFFFF (2147483647) indicates the line attenuation is out of range to be represented. A special value of 0x7FFFFFFE (2147483646) indicates the line attenuation measurement is unavailable. |
| Noise margin per band               | xdsl2LineBandStatusSnrMargin    | transmission.999.999.999.999.1.4  | SNR Margin is the maximum increase in dB of the noise power received at the xTU (xTU-R for a band in the downstream direction and xTU-C for a band in the upstream direction), such that the BER requirements are met for all bearer channels received at the xTU.  Values range from -640 to 630 in units of 0.1 dB (physical values are -64 to 63 dB). A special value of 0x7FFFFFFF (2147483647) indicates the SNR Margin is out of range to be represented. A special value of 0x7FFFFFFE (2147483646) indicates the SNR Margin measurement is currently unavailable.                                                                                                                                                                                     |
