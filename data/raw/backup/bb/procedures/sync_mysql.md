# Fix Mysql Replication

- [Fix Mysql Replication](#fix-mysql-replication)
  - [Scope](#scope)
    - [Glossary](#glossary)
  - [Setup](#setup)
    - [Mysql Instances](#mysql-instances)
      - [PR](#pr)
      - [DR](#dr)
  - [Procedure](#procedure)
    - [Identify the problem](#identify-the-problem)
    - [Repair MySQL Replication](#repair-mysql-replication)

## Scope

Sometimes there are invalid MySQL queries which cause the replication to not work anymore. In this short guide, it explained how you can repair the replication on the MySQL slave. This guide is for MySQL.

### Glossary

- MYSQL replication: It is a process that enables data from one MySQL database server (the master) to copied automatically to one or more MySQL database servers (the slaves)

## Setup

### Mysql Instances

#### PR

Mysql supported by Oracle and if any other issue occured a critical ticket should created on Oracle Support. **This instance is not supported by jkl Telecom S.A.**

**User**: `mysql`

**Port**: `3306`

**Password**: [prodsyspasswd.kbdx](/KnowledgeBase/prodsyspasswd.kdbx)

**Master Mysql Host**: `pr1node03.mno.gr`

**Slave Mysql Host**: `pr1node02.ngr.gr`

**Mysql Configuration**: `/etc/my.cnf`

**Mysql Data Path**: `/var/lib/mysql/`

**Mysql General Log File**: `/var/log/mysqld.log`

**Mysql Error Log File**: `/var/log/mysqld_error.log`

#### DR

**User**: `mysql`

**Port**: `3306`

**Password**: [prodsyspasswd.kbdx](/KnowledgeBase/prodsyspasswd.kdbx)

**Master Mysql Host**: `dr1node03.mno.gr`

**Slave Mysql Host**: `dr1node02.mno.gr`

**Mysql Configuration**: `/etc/my.cnf`

**Mysql Data Path**: `/var/lib/mysql/`

**Mysql General Log File**: `/var/log/mysqld.log`

**Mysql Error Log File**: `/var/log/mysqld_error.log`

## Procedure

### Identify the problem

1. From **Slave Mysql Host** as `root`:

      ```bash
      mysql -u root -p
      SHOW SLAVE STATUS\G;
      ```

2. If one of `Slave_IO_Running` or `Slave_SQL_Running` is set to `No`, then the replication is broken

### Repair MySQL Replication

1. From **Slave Mysql Host** as `root`:

      ```bash
      mysql -u root -p
	STOP SLAVE;
      ```

    - Just to go sure, we stop the slave:
	
      ``` bash
      SHOW SLAVE STATUS\G
      ```

    - Now both `Slave_IO_Running` & `Slave_SQL_Running` is set to `No`.
	
2. Restore from latest mysqldump backup:
    
	- From **Slave Mysql Host** as `root`:

      ```bash
      cd /backup
      ls -ltr
      tar -ztvf /backup/DRBDA_year-month-day.tar.gz | grep -i mysql_backup # List contents of the tar.gz file.Under backup folder stored tar.gz files from daily backup procedure,for both sites, with the format CLUSTER_year-month-day.tar.gz (e.g DRBDA_2022-03-21.tar.gz). This files contains several gz files combined in a tar.gz. Now we need to find the exact name of the gz backup file for mysql backup to proceed at next step.
      tar -zxvf /backup/DRBDA_year-month-day.tar.gz mysql_backup_yearmonthday.sql.gz # Untar from the tar.gz file the exact gz backup file for mysql backup that found from previous step. The exaxt name would be placed on mysql_backup_yearmonthday.sql.gz possition
      gunzip mysql_backup_yearmonthday.sql.gz # Decompress the file that untared from previous step
      mysql -uroot -p < mysql_backup_yearmonthday.sql
      ```

3. After succesfully restoration on **Slave Mysql Host** start slave:

      ``` bash
      mysql -u root -p
      SHOW SLAVE STATUS\G
      ```

      - No error should exist on `Last_Error`
      - If no error appeared then `START SLAVE`

      ```bash
      START SLAVE;
      ```
	  
4. Check if replication is working again
 
      ``` bash
      SHOW SLAVE STATUS\G
      ```

	- Both Slave_IO_Running and Slave_SQL_Running are set to `Yes` now. And the replication is running without any error.
	- `Seconds_Behind_Master` should be 0 after some minutes
