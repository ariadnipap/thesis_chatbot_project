---
title: Certificate Renewal Procedure for BigStreamer
description: Step-by-step guide to renew and validate Cloudera and HAProxy certificates across PR and DR environments, including certificate checks, backups, distribution, HAProxy replacement, and application restarts.
tags:
  - certificates
  - cloudera
  - haproxy
  - ssl
  - openssl
  - pem
  - jks
  - kudu
  - flows
  - cluster-maintenance
  - bigstreamer
  - edge-nodes
last_updated: 2025-05-01
author: ilpap
context:
  environment: BigStreamer
  sites:
    - PR
    - DR
  systems:
    - node01
    - dr1edge01
    - pr1edge01
    - Xr1node03
    - un1
    - edge nodes
  backup_paths:
    - /backup/new_certs/
    - /backup/haproxy_certs/
    - /opt/cloudera/security/
    - /opt/haproxy/security/
  services:
    - haproxy
    - kudu
    - spark flows
    - cloudera-scm-agent
    - cloudera-scm-server
    - bigdatamanager
---
# Certificate Renewal Procedure
Back up every certificate before doing any action
### Backup Procedure
- From node1 as root:
``` bash
dcli -C "cp -r /opt/cloudera/security /opt/cloudera/security.BAK_`date +%d%b%Y%H%M%S`" 
```
- From edge nodes as root:
```bash
cp -r /opt/haproxy/security /opt/haproxy/security.BAK_`date +%d%b%Y%H%M%S`
```
## Node and VIP Certificates check
This section explains how to verify unsigned and signed certificates for Cloudera and edge nodes using OpenSSL. Ensures certificate integrity before replacement.
### Check unsigned certificates
- In this step we checked the presigned certificates in `backup/new_certs/cert_requests` if they have correct subject with the following command: 
`openssl req -in new_certs/cert_requests/dr1edge.mno.gr-ert-file -noout -text`
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/certreq.JPG)
and also we check the modulus if it is the same. Basically we check the output of the following commands:
`openssl rsa -in /opt/cloudera/security/x509/node.key -noout -text modulus`
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/modulus1.JPG)
`openssl req -in new_certs/cert_requests/dr1edge.mno.gr-ert-file -noout -text -modulus`
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/modulus2.JPG)
Then we provide to the customer the certificates located in `backup/new_certs/cert_requests` in order to be signed
### Check signed certificates from mno
In the following folder are located the signed certificates
Backup NFS Folder: `/backup/new_certs/certificates`
Check the certificates in the above mentioned folder for issuer, subject, TLS Web, date.
The `'ln -1'` feature prints all files in the for loop per line
- Check the issuer
`for i in 'ln -1'; do echo $i; openssl x509 -noout -text -in $i | grep -i issuer ; done` 
In the above command we wait a return such as this: 
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/issuer.JPG)
- Check the subject
`for i in 'ln -1'; do echo $i; openssl x509 -noout -text -in $i | grep -i subject ; done`
In the above command we wait a return such as this:
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/subject.JPG)
- Check the TLS Web
`for i in 'ln -1'; do echo $i; openssl x509 -noout -text -in $i | grep -i 'TLS Web' ; done` 
In the above command we wait a return such as this: 
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/tls.JPG)
- Check the dates
`openssl x509 -noout -text -in 'cert_file' - dates`
In the above command we wait a return such as this: 
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/dates.JPG)
- Or with a for loop for all the files
`for i in 'ln -1'; do openssl x509 -noout -text -in $i | grep -i 'ndef after'; done`
In the above command we wait a return such as this: 
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/notafter.JPG)
### Haproxy certificates check and replacement
Backup NFS Folder: `/backup/haproxy_certs`
`ssh root@pr1edge01`
In order to set the new haproxy certificates we need to have 9 certificates
Check the haproxy security folder: `/opt/haproxy/security/x509/`
```
devsqla_mno_gr.haproxy.pem
pr1edge_mno_gr.haproxy.pem
dr1edge_mno_gr.haproxy.pem
qasqla_mno_gr.haproxy.pem
prodsqla_mno_gr.haproxy.pem
```
and the node certifate for PR and DR in the following format 
`node.haproxy.pem`
- Now in the NFS mentioned files we need to replace the second certificate with the one that is located in the signed cert files that the customer has send to us
`vi /backup/haproxy_certs/devsqla_mno_gr.haproxy.pem` and replace the 
```
--- BEGIN CERTIFICATE ---
... 
--- END CERTIFICATE ---
```
with the one located in `/backup/new_certs/certificates/devsqla_mno_gr-cert-file.cer`
- Moreover, as root replace the CERTIFICATE to the
`vi /backup/haproxy_certs/devsqla_mno_gr.haproxy.pem`
with the certificate from 
`cat /backup/new_certs/certificates/devsql_mno_gr-cert-file.cer` 
and copy the section:
```
    ---BEGIN CERTIFICATE---

    .....

    ---END CERTIFICATE---
```
and replace it with the certificate on the pem file `/backup/haproxy_certs/devsqla_mno_gr.haproxy.pem`
For all the other `pem` files we need to do the same procedure accordingly. **EVERY PEM HAS A UNIQUE CER FILE**
We need to specify in more detail the above steps especially for the 4 edge nodes we have on PR & DR sites.
- Firstly, under `/opt/haproxy/security/x509/` folder there is the `node.haproxy.pem` certificate as mentioned before. We must copy this file under the NFS mentioned folder `/backup/haproxy_certs/`.
For example:
```bash
cp /opt/haproxy/security/x509/node.haproxy.pem /backup/haproxy_certs/Xredge0X.node.haproxy.pem
```
- Then, from `/backup/haproxy_certs/Xredge0X.node.haproxy.pem` we must keep only the private key certificate section and replace the rest of the certificates with the ones that are located in the signed cert file `/backup/new_certs/certificates/Xr1edge0X_mno_gr-cert-file.cer` that the customer has sent to us.
- We must follow the same procedure for all edge nodes certificates.
#### Checks
- Check the issuer on previous certificates located in `/etc/pki/ca-trust/source/anchors/`
```
ca1.crt
ca.crt
ca3.crt
```
- Check the issuer in the above mentioned crt
`for i in ca1.crt ca3.crt ca.crt; do echo $i; openssl x509 -noout -text -in $i | grep -i issuer; done`
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/pki.JPG)
From the above image we excepted to see the issuer as `mnoInternalRoot` which is correct in `ca3.crt`.
- In order to check if the certificates has been signed from the same issuer. Run the following commands and check the output. It should be the same. If not, the certificate is wrong
```
openssl x509 -noout -modulus -in 'cert_file'
openssl rsa -noout -modulus -in 'cert_file'
```
![alt text](KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/media/x509.JPG)
### Actions Before Distributing the certificates
Explains how to safely stop Spark flows and prepare systems for certificate changes.
mno is obliged to move the traffic from PR site to DR site.
Stop the flows, as user PRODREST:
```
# Signal Spark flows to shut down safely before cert replacement
[PRODREST@Xr1edge01]# touch SHUTDOWN
[PRODREST@Xr1edge01]# hdfs dfs -put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest/topology_shutdown_marker/
[PRODREST@Xr1edge01]# hdfs dfs -put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest_Visible/topology_shutdown_marker/
[PRODREST@Xr1edge01]# hdfs dfs -put SHUTDOWN /user/PRODREST/service/PROD_Online_Ingest/topology_shutdown_marker/
```
Check that flows stopped.
```
[PRODREST@Xr1edge01]# yarn application -list | grep -i PROD_
```
When executing the same procedure on the DR site, we should **additionally** stop the following flows as user DEVREST:
```
[DEVREST@dr1edge01]# touch SHUTDOWN
[DEVREST@dr1edge01]# hdfs dfs -put SHUTDOWN /user/DEVREST/service/DEV_IBank_Ingest/topology_shutdown_marker/
[DEVREST@dr1edge01]# hdfs dfs -put SHUTDOWN /user/DEVREST/service/DEV_Online_Ingest/topology_shutdown_marker/
```
Check that flows stopped.
```
[DEVREST@dr1edge01]# yarn application -list | grep DEVREST
```
## Distribute the certificates
Covers how to copy, import, and activate the new signed certificates across all cluster nodes.
### Generate the keystore password (It's not the same for both sites)
`bdacli getinfo cluster_https_keystore_password`
From node01:
#### Node certificates
For internal nodes:
```
dcli -C cp /backup/new_certs/certificates/\$HOSTNAME-cert-file.cer /opt/cloudera/security/x509/node.cert
```
For edge nodes:
```
cp /backup/new_certs/cert_2024/$HOSTNAME-cert-file.cer /opt/cloudera/security/x509/node.cert
```
#### JKS certificates
For internal nodes:
```
# Import signed certificate into Cloudera's Java Keystore (JKS) on internal nodes
dcli -C keytool -import -file /opt/cloudera/security/x509/node.cert -alias \$HOSTNAME -keystore /opt/cloudera/security/jks/node.jks -storepass KEYSTORE_PASS_FROM_ABOVE -keypass KEYSTORE_PASS_FROM_ABOVE -noprompt
```
For edge nodes:
```
keytool -import -file /opt/cloudera/security/x509/node.cert -alias $HOSTNAME -keystore /opt/cloudera/security/jks/node.jks -storepass KEYSTORE_PASS_FROM_ABOVE -keypass KEYSTORE_PASS_FROM_ABOVE -noprompt
```
#### Check new certificates
For internal nodes:

```
dcli -C "keytool -list -v -keystore /opt/cloudera/security/jks/node.jks -alias \$HOSTNAME"
```
For edge nodes:
```
keytool -list -v -keystore /opt/cloudera/security/jks/node.jks -alias $HOSTNAME
```
#### Haproxy certificates
Copy the files from `/backup/haproxy_certs/` to `/opt/haproxy/security/x509/` and replace the existing ones.
**Special caution**:
Must copy `Xr1edge0X_mno_gr.node.haproxy.pem` that we created in the previous steps to the `node.haproxy.pem` certificate existing on the edge nodes
```
# Replace haproxy node certificate with newly signed one
cp /backup/haproxy_certs/Xr1edge0X_mno_gr.node.haproxy.pem /opt/haproxy/security/x509/node.haproxy.pem
```
**Do not copy root.inter.pem**
After copying the certificates, restart the haproxy service on both edge nodes
```
systemctl reload haproxy 
systemctl status haproxy
pcs resource cleanup haproxy-clone
```
If after restarting HAProxy the service fails due to missing chain or improper concatenation, rebuild the node certificate manually like this:
```
cd /opt/cloudera/security/x509
cat node.hue.key node.cert > /opt/haproxy/security/x509/node.haproxy.pem
```
### Actions After Distributing the certificates
Steps to restart agents and verify successful service recovery after new certificates are in place.
When the new certificates replace the old ones, the services of the cluster will become healthy. Restart is required. [Official Guide](https://docs.cloudera.com/documentation/enterprise/6/6.3/topics/cm_mc_start_stop_service.html)
All services except zookeeper need restart. The service `Bigdatamanager` should always remain stopped 
We prefer to start with Kudu because it takes longer to synchronize. Also, for KMS service perform restart 1 by 1. For KMS server perform restart on both passive services and then on both active.  
Lastlty, after Kudu syncs start the flows.
When the cluster be stopped then:
For edge nodes:
```
systemctl status cloudera-scm-agent
systemctl restart cloudera-scm-agent 
```
For internal nodes:
```
dcli -C "systemctl status cloudera-scm-agent | grep -i Active" 
# Restart Cloudera agents across all nodes to load new certificates
dcli -C "systemctl restart cloudera-scm-agent" 
dcli -C "systemctl status cloudera-scm-agent | grep -i Active"
```
```
dcli -c Xr1node03 "systemctl restart cloudera-scm-server" 
dcli -c Xr1node03 "systemctl status cloudera-scm-server"
```
### Kudu Checks
Open UIs from masters and tablets from internal firefox from edge nodes. Firefox launced with your personal Exxx account.
Logs from kudu logs on every node:
`tail -f /var/log/kudu/kudu-tserver.INFO` checks that the number will be equal to this number => `ls /u12/kudu/tablet/data/data/ | grep metadata | wc -l`, when the synchronization is successfully completed.
#### Start flows
Start ibank from edge Node as PRODREST
```
/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_stream_cluster_mno_STABLE.sh
```
Start ibank visible from edge Node as PRODREST
```
/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_stream_cluster_mno_VISIBLE_STABLE.sh
```
Start online from edge Node as PRODREST
```
/opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_stream_cluster_mno_STABLE.sh
```
Similarly from a DR edge node as DEVREST:
Start ibank
```
/opt/ingestion/DEVREST/ibank/spark/submit/submitmnoSparkTopology_stream_cluster_mno.sh
```
Start online
```
/opt/ingestion/DEVREST/online/spark/submit/submitmnoSparkTopology_stream_cluster_mno.sh
```
### Applications checks
When all Kudu Tablets are synchronized and **all flows are on RUNNING status** then:
as user PRODREST from an edge node:
```
impala-shell xr1edge.mno.gr -k -ssl
```
Execute the following query:
```
select max(timestamp) as time, 'ibank' as application from prod_trlog_ibank.service_audit_stream union select max(timestamp) as time, 'online' as application from prod_trlog_online.service_audit_stream;
```