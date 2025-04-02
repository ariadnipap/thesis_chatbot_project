# Postgres Upgrade

[[_TOC_]]

All procedures pertain to PR and DR edge nodes, except the RPM repository creation
which is performed on pr1node1:
- pr1edge01
- pr1edge02
- dr1edge01
- dr1edge02

## Preparation

Before continuing with the changes it is best to put the edge node you are
working on in standby mode, so as to not disrupt services:

    $ ssh Exxxx@XXXedgeXX
    $ sudo -i

And follow the procedures described in the **Switchover of Cluster Resources** chapter
of the **Security Vulnerabilities** MOP [here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx).

Stop the running postgres service:

    # sudo -iu postgres

    $ systemctl stop postgresql-9.5.service
    $ systemctl disable postgresql-9-5.service

    $ systemctl status postgresql-9.5.service

Backup data on each edge server:
- edge01: `$ pg_dumpall > edge01_postgres_backup`
- edge02: `$ pg_dumpall > edge02_postgres_backup`

Backup **pg_hba.conf** and **postgresql.conf**:

    # cp -ap /var/lib/psql/9.5/data/pg_hba.conf /var/lib/psql/9.5/data/pg_hba.conf.bak
    # cp -ap /var/lib/psql/9.5/data/postgresql.conf /var/lib/psql/9.5/data/postgresql.conf.bak

### Repositories Creation

Download rpms for Postgres 14 from the Postgres site
https://download.postgresql.org/pub/repos/yum/14/redhat/rhel-7.9-x86_64/.....
and prepare the new postgres repository on pr1node01:

    $ ssh Exxxx@pr1node01
    $ sudo -i
    # mkdir -p /var/www/postgres14/Packages/

Move all the rpm files of Postgres14 under `/var/www/html/postgres14/Packages` and
create the **YUM** repository:

    # cd /var/www/postgres14/
    # createrepo .

or if the repository existed:

    # createrepo --update .

Create the repository file on one of the edge nodes and copy it to all others:

    $ ssh Exxx@pr1edge01
    $ sudo -i

    # vi /etc/yum.repos.d/postgres14.repo
    [postgres14]
    name = Postgres14
    baseurl =  http://pr1node01.mno.gr/postgres14/
    enabled = 1
    gpgcheck = 0

    # scp /etc/yum.repos.d/postgres14.repo XXXedgeXX:/etc/yum.repos.d/


On each edge node disable the old postgres repositorry by setting `enabled = 0` inside
its repo file under `/etc/yum.repos.d/`.

## Execution

Perform the update using **YUM**, while enabling the repository for the new Postgres
and disabling the previous repository if exists on each edge node:

    $ ssh Exxxx@XXXedgeXX
    $ sudo -i

    # yum clean all
    # yum install --disablerepo=* --enablerepo=postgres14 postgresql14 postgresql14-server postgresql14-contrib postgresql14-libs

Change the data directory and setup the newly updated PostgreSQL:

    # vi usr/lib/systemd/system/postgresql-14.service
    Environment=PGDATA=/var/lib/pgsql/9.14/data

    # /usr/pgsql-14/bin/postgresql-14-setup initdb
    # systemctl enable --now postgresql-14

Login to each edge node and restore data from backup:

    $ ssh Exxx@XXXedgeXX:
    $ sudo -iu postgres

    $ psql -f edgeXX_postgres_backup postgres

    $ systemctl restart postgresql-14.service
    $ systemctl status postgresql-14.service

Check **pg_hba.conf** and **postgresql.conf** for differencies between versions:

    $ sdiff /var/lib/pgsql/9.14/data/pg_hba.conf /var/lib/psql/9.5/data/pg_hba.conf
    $ sdiff /var/lib/pgsql/9.14/data/postgresql.conf /var/lib/psql/9.5/data/postgresql.conf

If everything is ok, unstandby the node

## Rollback

Login to each edge node, stop the postgres service and downgrade using **YUM**:

    $ ssh Exxx@XXXedgeXX:
    $ sudo -iu postgres

    $ systemctl disable --now postgresql-14.service
    $ systemctl status postgresql-14.service

    $ sudo -i
    # yum clean all
    # yum downgrade --disablerepo=* --enablerepo=postgres9 postgresql

    # systemctl enable --now postgresql-9-5.service
