# Manage Kafka MirrorMaker

## Description
This document outlines the procedure for managing Kafka MirrorMaker, including stopping, starting, and committing consumer group offsets to prevent data replay issues.

## Prerequisites
- Administrator privileges on **Cloudera Manager**.
- SSH access to Kafka nodes.
- Knowledge of Kafka consumer groups and topics.
- Kerberos authentication (`kinit`) for Kafka.

## Procedure Steps

### 1. Stop Kafka MirrorMakers for PR Site

#### a. Stop Primary Site MirrorMakers:
From the **Primary Site Cloudera Manager**:
```
PRBDA > Kafka > Instances
Select MirrorMakers on nodes: pr1node01, pr1node04, pr1node05, pr1node06
Stop
```

#### b. Stop Disaster Site MirrorMakers:
From the **Disaster Site Cloudera Manager**:
```
DRBDA > Kafka > Instances
Select MirrorMakers on nodes: dr1node05, dr1node06
Stop
```

---

### 2. Stop Kafka MirrorMakers for DR Site

#### a. Stop Primary Site MirrorMakers:
From the **Primary Site Cloudera Manager**:
```
DRBDA > Kafka > Instances
Select MirrorMakers on nodes: dr1node01, dr1node04, dr1node05, dr1node06
Stop
```

#### b. Stop Disaster Site MirrorMakers:
From the **Disaster Site Cloudera Manager**:
```
PRBDA > Kafka > Instances
Select MirrorMakers on nodes: pr1node05, pr1node06
Stop
```

---

### 3. Commit Consumer Groups Offsets for PR Site

#### a. Create `group.properties`:
```conf
security.protocol=SASL_SSL
sasl.kerberos.service.name=kafka
```

#### b. Create `jaas.conf`:
```conf
Client {
  com.sun.security.auth.module.Krb5LoginModule required
  useKeyTab=false
  useTicketCache=true
  doNotPrompt=true
  principal="kafka@BDAP.mno.GR";
};

KafkaClient {
  com.sun.security.auth.module.Krb5LoginModule required
  useKeyTab=false
  useTicketCache=true
  doNotPrompt=true
  principal="kafka@BDAP.mno.GR"
  service="kafka";
};
```

#### c. Log in to Kerberos and configure security:
```bash
kinit kafka@BDAP.mno.GR
export KAFKA_JVM_PERFORMANCE_OPTS="-Djava.security.auth.login.config=./jaas.conf"
```

#### d. Commit offsets:
```bash
export DATETIME=1970-01-01T00:00:00.000Z
kafka-consumer-groups --bootstrap-server pr1node01.mno.gr:9093,pr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-002 --all-topics --reset-offsets --to-datetime $DATETIME --execute
```

---

### 4. Commit Consumer Groups Offsets for DR Site

#### a. Create `group.properties`:
```conf
security.protocol=SASL_SSL
sasl.kerberos.service.name=kafka
```

#### b. Create `jaas.conf`:
```conf
Client {
  com.sun.security.auth.module.Krb5LoginModule required
  useKeyTab=false
  useTicketCache=true
  doNotPrompt=true
  principal="kafka@BDAD.mno.GR";
};

KafkaClient {
  com.sun.security.auth.module.Krb5LoginModule required
  useKeyTab=false
  useTicketCache=true
  doNotPrompt=true
  principal="kafka@BDAD.mno.GR"
  service="kafka";
};
```

#### c. Log in to Kerberos and configure security:
```bash
kinit kafka@BDAD.mno.GR
export KAFKA_JVM_PERFORMANCE_OPTS="-Djava.security.auth.login.config=./jaas.conf"
```

#### d. Commit offsets:
```bash
export DATETIME=1970-01-01T00:00:00.000Z
kafka-consumer-groups --bootstrap-server dr1node01.mno.gr:9093,dr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-002 --all-topics --reset-offsets --to-datetime $DATETIME --execute
```

---

### 5. Start Kafka MirrorMakers for PR Site

#### a. Start Primary Site MirrorMakers:
From the **Primary Site Cloudera Manager**:
```
PRBDA > Kafka > Instances
Select MirrorMakers on nodes: pr1node01, pr1node04, pr1node05, pr1node06
Start
```
#### b. Start Disaster Site MirrorMakers:
From the **Disaster Site Cloudera Manager**:
```
DRBDA > Kafka > Instances
Select MirrorMakers on nodes: dr1node05, dr1node06
Start
```

---

### 6. Start Kafka MirrorMakers for DR Site

#### a. Start Primary Site MirrorMakers:
From the **Disaster Site Cloudera Manager**:
```
DRBDA > Kafka > Instances
Select MirrorMakers on nodes: dr1node01, dr1node04, dr1node05, dr1node06
Start
```
#### b. Start Disaster Site MirrorMakers:
From the **Primary Site Cloudera Manager**:
```
PRBDA > Kafka > Instances
Select MirrorMakers on nodes: pr1node05, pr1node06
Start
```

---

## Actions Taken / Expected Output
- Kafka MirrorMaker processes are stopped and restarted properly.
- Consumer group offsets are committed successfully.
- Traffic flow is restored.

## Notes and Warnings
> - Ensure consumer groups are **inactive** before committing offsets.
> - Restarting MirrorMaker may cause temporary data delays.
> - Double-check `DATETIME` for accurate offset resets.

## Affected Systems / Scope
- **Kafka clusters** in the Primary and Disaster Recovery sites.
- **MirrorMaker consumer groups** for Internet Banking and Online Applications.

## Troubleshooting / Error Handling

### Common Issues:
- **Issue:** Kafka MirrorMaker does not restart.  
  **Solution:** Check logs and restart manually.

- **Issue:** Consumer group offsets do not update.  
  **Solution:** Ensure MirrorMakers are stopped before committing offsets.

- **Issue:** Data replay issues after restart.  
  **Solution:** Verify offset commit time (`DATETIME`) before execution.

### Log File Locations:
```bash
tail -f /var/log/kafka/*.log
```

## References
- [Cloudera Documentation](https://www.cloudera.com/)

