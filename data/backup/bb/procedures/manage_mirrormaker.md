# Manage Kafka MirrorMaker

- [Manage Kafka MirrorMaker](#manage-kafka-mirrormaker)
  - [Scope](#scope)
  - [Setup](#setup)
  - [Procedure](#procedure)
    - [Stop Kafka MirrorMakers for PR site](#stop-kafka-mirrormakers-for-pr-site)
    - [Stop Kafka MirrorMakers for DR site](#stop-kafka-mirrormakers-for-dr-site)
    - [Commit Consumer Groups Offsets for PR site](#commit-consumer-groups-offsets-for-pr-site)
    - [Commit Consumer Groups Offsets for DR site](#commit-consumer-groups-offsets-for-dr-site)
    - [Start Kafka MirrorMakers for PR site](#start-kafka-mirrormakers-for-pr-site)
    - [Start Kafka MirrorMakers for DR site](#start-kafka-mirrormakers-for-dr-site)
  - [Ndefs](#ndefs)

## Scope

Kafka MirrorMaker has been configured with auto.offsets.reset=false. This means that the MirrorMaker consumers never commit the offsets.
If the MirrorMakers' consumer group goes inactive(both MirrorMakers are offline at the same time), their consumer group will reset to the earliest offset available.
This means that the last week will be mirrored to the final topic and will be replayed by the Spark streaming topology.
This document describes how to commit the offsets for the MirrorMaker consumer groups, in order to avoid this issue.

## Setup

1. MirrorMakers on nodes pr1node01 and pr1node04:

    - Replicate the traffic from the **Primary Site Mirror Topics** to the **Primary Site Final Topics**.
    - Replicate Production Topics for both Internet Banking and Online Applications.
    - Use **mir-trlog-ingest-stream-con-002** consumer group.
    - Offsets are committed to the **Primary Site Kafka cluster**.

2. MirrorMakers on nodes pr1node05 and pr1node06:
  
    - Replicate the traffic from the **Disaster Site Mirror Topics** to the **Primary Site Final Topics**.
    - Replicate Production Topics for both Internet Banking and Online Applications.
    - Use **mir-trlog-ingest-stream-con-001** consumer group.
    - Offsets are committed to the **Disaster Site Kafka cluster**.

3. MirrorMakers on nodes dr1node01 and dr1node04:

    - Replicate the traffic from the **Disaster Site Mirror Topics** to the **Disaster Site Final Topics**.
    - Replicate Production Topics for both Internet Banking and Online Applications.
    - Use **mir-trlog-ingest-stream-con-002** consumer group.
    - Offsets are committed to the **Disaster Site Kafka cluster**.

4. MirrorMakers on nodes dr1node05 and dr1node06:
  
    - Replicate the traffic from the **Primary Site Mirror Topics** to the **Disaster Site Final Topics**.
    - Replicate Production Topics for both Internet Banking and Online Applications.
    - Use **mir-trlog-ingest-stream-con-001** consumer group.
    - Offsets are committed to the **Primary Site Kafka cluster**.

## Procedure

### Stop Kafka MirrorMakers for PR site

1. Stop Primary Site MirrorMakers:

    From the Primary Site Cloudera Manager with a user that has administrator privileges:

    - PRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes pr1node01,pr1node04,pr1node05 and pr1node06
    - Stop

2. Stop Disaster Site MirrorMakers:

    From the Disaster Site Cloudera Manager with a user that has administrator privileges:

    - DRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes dr1node05 and dr1node06
    - Stop

### Stop Kafka MirrorMakers for DR site

1. Stop Primary Site MirrorMakers:

    From the Primary Site Cloudera Manager with a user that has administrator privileges:

    - DRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes dr1node01,dr1node04,dr1node05 and dr1node06
    - Stop

2. Stop Disaster Site MirrorMakers:

    From the Disaster Site Cloudera Manager with a user that has administrator privileges:

    - PRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes pr1node05 and pr1node06
    - Stop

### Commit Consumer Groups Offsets for PR site

The following steps can be performed at any node of the Primary Site cluster. The consumer groups need to be **inactive** for these action to be performed.

1. Create a file named group.properties:

    ``` conf
    security.protocol=SASL_SSL
    sasl.kerberos.service.name=kafka
    ```

2. Create a file named jaas.conf:

    ``` conf
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

3. Log in to kerberos as the **_kafka@BDAP.mno.GR_** principal and configure security:

    ``` bash
    kinit kafka@BDAP.mno.GR
    export KAFKA_JVM_PERFORMANCE_OPTS="-Djava.security.auth.login.config=./jaas.conf"
    ```

4. Commit the offsets for all relevant consumer groups:

    ``` bash
    export DATETIME=1970-01-01T00:00:00.000Z #UTC time. See ndefs
    kafka-consumer-groups --bootstrap-server pr1node01.mno.gr:9093,pr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-002 --all-topics --reset-offsets --to-datetime $DATETIME --execute
    kafka-consumer-groups --bootstrap-server pr1node01.mno.gr:9093,pr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-001 --all-topics --reset-offsets --to-datetime $DATETIME --execute
    kafka-consumer-groups --bootstrap-server dr1node01.mno.gr:9093,dr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-001 --all-topics --reset-offsets --to-datetime $DATETIME --execute
    ```

### Commit Consumer Groups Offsets for DR site

The following steps can be performed at any node of the Disaster Site cluster. The consumer groups need to be **inactive** for these action to be performed.

1. Create a file named group.properties:

    ``` conf
    security.protocol=SASL_SSL
    sasl.kerberos.service.name=kafka
    ```

2. Create a file named jaas.conf:

    ``` conf
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

3. Log in to kerberos as the **_kafka@BDAD.mno.GR_** principal and configure security:

    ``` bash
    kinit kafka@BDAD.mno.GR
    export KAFKA_JVM_PERFORMANCE_OPTS="-Djava.security.auth.login.config=./jaas.conf"
    ```

4. Commit the offsets for all relevant consumer groups:

    ``` bash
    export DATETIME=1970-01-01T00:00:00.000Z #UTC time. See ndefs
    kafka-consumer-groups --bootstrap-server dr1node01.mno.gr:9093,dr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-002 --all-topics --reset-offsets --to-datetime $DATETIME --execute
    kafka-consumer-groups --bootstrap-server dr1node01.mno.gr:9093,dr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-001 --all-topics --reset-offsets --to-datetime $DATETIME --execute
    kafka-consumer-groups --bootstrap-server pr1node01.mno.gr:9093,pr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-001 --all-topics --reset-offsets --to-datetime $DATETIME --execute
    ```

### Start Kafka MirrorMakers for PR site

1. Start Primary Site MirrorMakers:

    From the Primary Site Cloudera Manager with a user that has administrator privileges:

    - PRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes pr1node01,pr1node04,pr1node05 and pr1node06
    - Start

    All messages should be consumed in about one to two minutes.

2. Start Disaster Site MirrorMakers:

    From the Disaster Site Cloudera Manager with a user that has administrator privileges:
    - DRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes dr1node05 and dr1node06
    - Start

    Wait for traffic on all topics to get back to normal values before any changes.

### Start Kafka MirrorMakers for DR site

1. Start Primary Site MirrorMakers:

    From the Disaster Site Cloudera Manager with a user that has administrator privileges:

    - DRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes dr1node01,dr1node04,dr1node05 and dr1node06
    - Start

    All messages should be consumed in about one to two minutes.

2. Start Disaster Site MirrorMakers:

    From the Primary Site Cloudera Manager with a user that has administrator privileges:

    - PRBDA > Kafka > Instances
    - Select the MirrorMakers running on nodes pr1node05 and pr1node06
    - Start

    Wait for traffic on all topics to get back to normal values before any changes.

## Ndefs

- The result from the following queries can be useful during startup:

    ``` sql
    SELECT min(`timestamp`),max(`timestamp`) FROM prod_trlog_ibank.service_audit_stream
    SELECT min(`timestamp`),max(`timestamp`) FROM prod_trlog_online.service_audit_stream
    ```

- Consider committing offsets at a time 5 minutes prior to max timestamp
- Time should be in UTC e.g. 2019-09-02T12:30:00.000Z = 2019-09-02T15:30:00.000 EEST
- The option _--all-topics_ commits the offsets **only** for the topics this consumer group has ever subscribed and not all the topics of the Kafka cluster
- These commands are only for consumers that use the new API (version 0.10 and later)
- The following commands can be useful:

    ``` bash
    export DATETIME=1970-01-01T00:00:00.000Z
    kafka-consumer-groups --bootstrap-server dr1node01.mno.gr:9093,dr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-002 --all-topics --describe # List offsets
    kafka-consumer-groups --bootstrap-server dr1node01.mno.gr:9093,dr1node02.mno.gr:9093 --command-config group.properties --group mir-trlog-ingest-stream-con-002 --all-topics --reset-offsets --to-datetime $DATETIME # Dry run
    ```
