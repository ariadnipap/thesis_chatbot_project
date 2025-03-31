# Certificate Renewal Procedure

## Description
This procedure details the steps required to renew certificates for Cloudera and HAProxy environments, ensuring service continuity.

## Prerequisites
- Access to Cloudera and HAProxy nodes with root privileges.
- Backup of existing certificates.
- Signed certificates from MNO.
- Ability to restart services after replacement.

## Procedure Steps

### 1. Backup Procedure

#### From node1 as root:

dcli -C "cp -r /opt/cloudera/security /opt/cloudera/security.BAK_date +%d%b%Y%H%M%S"


#### From edge nodes as root:

cp -r /opt/haproxy/security /opt/haproxy/security.BAK_date +%d%b%Y%H%M%S


---

### 2. Node and VIP Certificates Check

#### Check unsigned certificates:

openssl req -in new_certs/cert_requests/dr1edge.mno.gr-ert-file -noout -text openssl rsa -in /opt/cloudera/security/x509/node.key -noout -text -modulus openssl req -in new_certs/cert_requests/dr1edge.mno.gr-ert-file -noout -text -modulus


Then, provide the customer with certificates located in `backup/new_certs/cert_requests` to be signed.

#### Check signed certificates from MNO:

for i in ls -1; do echo $i; openssl x509 -noout -text -in $i | grep -i issuer ; done for i in ls -1; do echo $i; openssl x509 -noout -text -in $i | grep -i subject ; done for i in ls -1; do echo $i; openssl x509 -noout -text -in $i | grep -i 'TLS Web' ; done for i in ls -1; do openssl x509 -noout -text -in $i | grep -i 'not after'; done


---

### 3. HAProxy Certificates Check and Replacement

#### Backup NFS Folder:  

/backup/haproxy_certs


#### SSH into HAProxy:

ssh root@pr1edge01


#### Required certificates:
- devsqla_mno_gr.haproxy.pem
- pr1edge_mno_gr.haproxy.pem
- dr1edge_mno_gr.haproxy.pem
- qasqla_mno_gr.haproxy.pem
- prodsqla_mno_gr.haproxy.pem
- node.haproxy.pem

#### Replace certificates:

vi /backup/haproxy_certs/devsqla_mno_gr.haproxy.pem

Replace:

--- BEGIN CERTIFICATE --- ... --- END CERTIFICATE ---

With the one from:

/backup/new_certs/certificates/devsqla_mno_gr-cert-file.cer

Repeat for all required `.pem` files.

---

### 4. Actions Before Distributing the Certificates

#### Move traffic from PR to DR site.

Stop flows as user **PRODREST**:

[PRODREST@Xr1edge01]# touch SHUTDOWN [PRODREST@Xr1edge01]# hdfs dfs –put SHUTDOWN /user/PRODREST/service/PROD_IBank_Ingest/topology_shutdown_marker/ [PRODREST@Xr1edge01]# yarn application –list | grep -i PROD_


Stop flows as user **DEVREST** for DR site:

[DEVREST@dr1edge01]# touch SHUTDOWN [DEVREST@dr1edge01]# hdfs dfs –put SHUTDOWN /user/DEVREST/service/DEV_IBank_Ingest/topology_shutdown_marker/ [DEVREST@dr1edge01]# yarn application –list | grep DEVREST


---

### 5. Distribute the Certificates

#### Generate keystore password:

bdacli getinfo cluster_https_keystore_password


#### Node certificates:

dcli -C cp /backup/new_certs/certificates/$HOSTNAME-cert-file.cer /opt/cloudera/security/x509/node.cert


For edge nodes:

cp /backup/new_certs/cert_2024/$HOSTNAME-cert-file.cer /opt/cloudera/security/x509/node.cert


#### JKS certificates:
For internal nodes:

dcli -C keytool -import -file /opt/cloudera/security/x509/node.cert -alias $HOSTNAME -keystore /opt/cloudera/security/jks/node.jks -storepass KEYSTORE_PASS_FROM_ABOVE -keypass KEYSTORE_PASS_FROM_ABOVE -noprompt

For edge nodes:

keytool -import -file /opt/cloudera/security/x509/node.cert -alias $HOSTNAME -keystore /opt/cloudera/security/jks/node.jks -storepass KEYSTORE_PASS_FROM_ABOVE -keypass KEYSTORE_PASS_FROM_ABOVE -noprompt


---

### 6. Restart Services and Kudu Checks

#### Restart services:

systemctl restart cloudera-scm-agent systemctl restart cloudera-scm-server


#### Kudu Synchronization:

tail -f /var/log/kudu/kudu-tserver.INFO ls /u12/kudu/tablet/data/data/ | grep metadata | wc -l

Ensure the counts match before proceeding.

---

### 7. Start Flows and Application Checks

#### Start Flows:
Start ibank:

/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_stream_cluster_mno_STABLE.sh


Start ibank visible:

/opt/ingestion/PRODREST/ibank/spark/submit/submitmnoSparkTopology_stream_cluster_mno_VISIBLE_STABLE.sh


Start online ingestion:

/opt/ingestion/PRODREST/online/spark/submit/submitmnoSparkTopology_stream_cluster_mno_STABLE.sh


#### Application checks:

impala-shell xr1edge.mno.gr -k -ssl

Execute the query:

select max(timestamp) as time, 'ibank' as application from prod_trlog_ibank.service_audit_stream union select max(timestamp) as time, 'online' as application from prod_trlog_online.service_audit_stream;


---

## Actions Taken / Expected Output
- Old certificates are backed up.
- New certificates are distributed and applied correctly.
- Services restart successfully, and cluster functions without issues.
- Kudu synchronization completes successfully.
- Flows start and execute as expected.

---

## Notes and Warnings
> Ensure traffic is shifted from PR to DR before applying new certificates.  
> Restart all services except **Zookeeper** and **Bigdatamanager**.  
> Ensure Kudu syncs before starting flows.  
> Do not copy `root.inter.pem` in HAProxy certificates.  

---

## Affected Systems / Scope
- Cloudera security certificates
- HAProxy security certificates
- Application flows relying on Kudu

---

## Troubleshooting / Error Handling
- If HAProxy certificates cause issues:

cd /opt/cloudera/security/x509 cat node.hue.key node.cert > /opt/haproxy/security/x509/node.haproxy.pem

- If flows do not restart, verify service logs:

tail -f /var/log/haproxy.log tail -f /var/log/cloudera-scm-agent/cloudera-scm-agent.log


---

## References
- [Cloudera Service Restart Guide](https://docs.cloudera.com/documentation/enterprise/6/6.3/topics/cm_mc_start_stop_service.html)

