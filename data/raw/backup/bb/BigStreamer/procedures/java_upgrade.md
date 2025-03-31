# Java Upgrade Procedure

## Description
This document outlines the upgrade process for the minor version of Oracle Java 1.8 on **mno's edge nodes**. The procedure applies to **PR and DR edge nodes**, except for the **RPM repository creation**, which is performed on **pr1node1**.

### Affected Edge Nodes:
- pr1edge01
- pr1edge02
- dr1edge01
- dr1edge02

## Prerequisites
- Root access to the necessary systems.
- Access to [Oracle Java SE Archive Downloads](https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html) to download the required RPMs.
- Ensure backup of existing Java installations.
- Access to the **Security Vulnerabilities** MOP for switchover of cluster resources.

## Procedure Steps

### 1. Repository Creation (Performed on **pr1node01**)
This step is performed once, as all future RPMs will be placed inside this repository.

#### a. SSH into **pr1node01** and create the repository directories:
```bash
$ ssh Exxxx@pr1node01
$ sudo -i
# mkdir -p /var/www/html/oracle_java/Packages
```

#### b. Download the desired RPMs from [Oracle Java SE Archive Downloads](https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html), place them inside /var/www/html/oracle_java/Packages, and create the repository:

```bash
cd /var/www/html/oracle_java
createrepo .
```

#### c. SSH into one of the edge nodes, create the yum repo file, and copy it to all other edge nodes:

```bash
$ ssh Exxx@pr1edge01
$ sudo -i
vi /etc/yum.repos.d/oracle_java.repo
```

Add the following content:

```ini
[oracle_java]
name = oracle_java
baseurl = http://p1node01.mno.gr/oracle_java
enabled = 1
gpgcheck = 0
```

Copy the repository file to all other edge nodes:

```bash
scp /etc/yum.repos.d/oracle_java.repo XXXedgeXX:/etc/yum.repos.d/
```

#### d. Install the Java package on each edge node:

```bash
# yum clean all
# yum install jdk-1.8
```

### 2. Repository Update
#### a. Download the required Java RPM version from Oracle Java SE Archive Downloads or Oracle Java SE Downloads and place it inside /var/www/html/oracle_java/Packages on pr1node01.
#### b. Update the repository:

```bash
$ ssh Exxxx@pr1node01
$ sudo -i
# cd /var/www/html/oracle_java
# createrepo --update .
```

### 3. Edge Host Update
#### Preparation

Before upgrading the edge nodes:

    Move their resources to other nodes.
    Create a backup of the existing Java installation.

Login to each edge node and execute:

```bash
$ ssh Exxxx@XXXedgeXX
$ sudo -i
# cp -rap /usr/java/jdk1.8.0_<old version>-amd64/ /usr/java/jdk1.8.0_<old version>-amd64.bak/
```

Refer to the Switchover of Cluster Resources chapter in the Security Vulnerabilities MOP for resource switchover:
https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx
#### Execution

Update the Java package using YUM on each edge node:

```bash
yum clean all
yum update java-1.8
```

#### Post-Update Configuration

    Copy old certificates into the new Java installation:

```bash
# cp -ap /usr/java/jdk1.8.0_<old version>-amd64.bak/jre/lib/security/jssecacerts \
    /usr/java/jdk1.8.0_<new version>-amd64/jre/lib/security/
```

    Run the update alternatives tool and input the new version when prompted:

```bash
# update-alternatives --config java
# update-alternatives --config javac
```
    Verify Java version:

```bash
# java -version
```

#### Final Checks

    Unstandby the node.
    Verify Wildfly logs for errors:
        **Server logs**: /var/log/wildfly/*/server.log (Ensure there are no undeployed WARs)
        **Access logs**: /var/log/wildfly/*/access.log (Ensure all responses report HTTP 200 status)

For detailed Wildfly management instructions, refer to:
[Wildfly Management Guide](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/manage_wildfly.md).
### 4. Rollback Procedure

In case the upgrade fails, rollback by switching back to the previous Java version.

    SSH into the affected edge node:

```bash
$ ssh Exxxx@XXXedgeXX
$ sudo -i
```

    Use update-alternatives to switch to the previous Java version:

```bash
# update-alternatives --config java
# update-alternatives --config javac
```

    Verify the rollback:

```bash
# java -version
```

## Actions Taken / Expected Output

    Java version is upgraded on all edge nodes.
    Wildfly services continue operating without issues.
    Verification of successful upgrade through logs.

## Notes and Warnings

        Always backup the old Java installation before proceeding.
        Ensure that cluster resources are properly switched before performing the upgrade.
        Double-check the repository and RPM versions before proceeding.

## Affected Systems / Scope

    Systems impacted: All PR and DR edge nodes running Oracle Java 1.8.
    Primary system for repository creation: pr1node01.

## Troubleshooting / Error Handling
### Common Issues and Solutions:

- Issue: Java version does not update after installation.
        Solution: Ensure that update-alternatives has been set to the new version.
- Issue: Wildfly services fail after upgrade.
        Solution: Check /var/log/wildfly/*/server.log and /var/log/wildfly/*/access.log for errors.
- Issue: Repository update fails.
        Solution: Verify that the RPM file is correctly placed and createrepo --update . has been executed.

### Log File Locations:

Check logs to debug issues:

```bash
# tail -f /var/log/wildfly/*/server.log
# tail -f /var/log/wildfly/*/access.log
```

## References

- [Oracle Java SE Archive Downloads](https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html)
- [Oracle Java SE Downloads](https://www.oracle.com/java/technologies/downloads/)
- [Security Vulnerabilities MOP](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)
- [Wildfly Management Guide](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/manage_wildfly.md)
