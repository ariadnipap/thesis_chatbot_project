# Java Upgrade

[[_TOC_]]

This document outlines the upgrade process of minor java version for Oracle Java 1.8
on mno's edge nodes. All procedures pertain to PR and DR edge nodes, except the RPM repository
creation which is performed on pr1node1:
- pr1edge01
- pr1edge02
- dr1edge01
- dr1edge02

## Repository Creation

This step only needs to be performed once as all subsequent RPM's will be placed inside this
repository. SSH into **p1node01** and as root create the repository directories:

    $ ssh Exxxx@pr1node01
    $ sudo -i
    # mkdir -p /var/www/html/oracle_java/Packages

Download the desired RPMs from [Oracle Java SE Archive Downloads](https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html), place them inside
`/var/www/html/oracle_java/Packages` and create the repository:

    # cd /var/www/html/oracle_java
    # createrepo .

SSH into one of the edge nodes, create the corresponding yum repo file and **scp** it into
all other edge nodes:

    $ ssh Exxx@pr1edge01
    $ sudo -i

    # vi /etc/yum.repos.d/oracle_java.repo
    [oracle_java]
    name = oracle_java
    baseurl =  http://p1node01.mno.gr/oracle_java
    enabled = 1
    gpgcheck = 0

    # scp /etc/yum.repos.d/oracle_java.repo XXXedgeXX:/etc/yum.repos.d/

Finally on each edge node install the above packages:

    # yum clean all
    # yum install jdk-1.8

## Repository Update

Download the desired version of Oracle Java 8 from
[Oracle Java SE Archive Downloads](https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html) or
[Oracle Java SE Downloads](https://www.oracle.com/java/technologies/downloads/) and
place the RPMs inside `/var/www/html/oracle_java/Packages` of **pr1node01**. Login to
**pr1node01** and update the repository with the new packages:

    $ ssh Exxxx@pr1node01
    $ sudo -i
    # cd /var/www/html/oracle_java
    # createrepo --update .

## Edge Host Update

### Preparation

Before upgrading the edge nodes, their resources must be moved to other nodes and a backup
of the old java be made. Login to each edge node:

    $ ssh Exxxx@XXXedgeXX
    $ sudo -i

    # cp -rap /usr/java/jdk1.8.0_<old version>-amd64/  /usr/java/jdk1.8.0_<old version>-amd64.bak/

And follow the procedures described in the **Switchover of Cluster Resources** chapter
of the **Security Vulnerabilities** MOP [here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx).

### Execution

Inside each edge node, update the java package using **YUM**:

    # yum clean all
    # yum update java-1.8

Copy the old certificates into the new installation directory and run the update alternatives
tool where you input the new version when prompted:

    # cp -ap /usr/java/jdk1.8.0_<old version>-amd64.bak/jre/lib/security/jssecacerts \
        /usr/java/jdk1.8.0_<new version>-amd64/jre/lib/security/
    # update alternatives --config java * javac

    # java -version

If everything is OK unstandby the node and check each wildfly instance's access and
server logs for the following:
- `/var/log/wildfly/*/server.log`: There are no undeployed WARs
- `/var/log/wildfly/*/access.log`: Everything is reporting HTTP 200 status

Detailed wildfly information and management instructions can be found
[here](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/mno/BigStreamer/supportDocuments/procedures/manage_wildfly.md).

## Rollback

Login to each edge node and downgrade using the update-alternatives and inputting the
previous version:

    $ ssh Exxxx@XXXedgeXX
    $ sudo -i

    # update alternatives --config java * javac

    # java -version
