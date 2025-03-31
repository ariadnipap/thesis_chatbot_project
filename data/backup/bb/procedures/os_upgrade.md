# OS Upgrade

[[_TOC_]]

All procedures pertain to PR and DR edge nodes:
- pr1edge01
- pr1edge02
- dr1edge01
- dr1edge02

## Updating within the same OS version

OS packages are sourced from the mno Nexus Repository, which in itself is a yum proxy
to the official oracle repositories for Oracle Linux 7.9. As such updating them requires only putting
an edge node on standby and updating through **YUM**:


    $ ssh Exxxx@XXXedgeXX
    $ sudo -i

Follow the procedures described in the **Switchover of Cluster Resources** chapter
of the **Security Vulnerabilities** MOP [here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx).

    # yum clean all
    # yum check-update

After reviewing the packages that will be updated continue with the update and after it is
complete unstandby the node:

    # yum update
    # systemctl reboot
    # cat /etc/oracle-release

## Rollback

Login to each edge node nad downgrade using **YUM**:

    $ ssh Exxxx@XXXedgeXX
    $ sudo -i

    # yum clean all
    # yum downgrade
    # reboot

    # cat /etc/oracle-release

## Nexus Repositories

Make sure that OS packages are sourced from the already setup Nexus repository.
Login to each edge node and edit/create the following repositories accordingly:

    $ ssh Exxxxx@XXXedgeXX
    $ sudo –i
    # cd /etc/yum.repos.d

    # vi el7_uek_latest.repo
    [el7_uek_latest]
    name = el7_uek_latest
    baseurl = http://999.999.999.999:8081/repository/el7_uek_latest/
    enabled = 1
    gpgcheck = 0
    exclude=postgresql*

    # vi uek_release_4_packages.repo
    [uek_release_4_packages]
    name = uek_release_4_packages
    baseurl = http://999.999.999.999:8081/repository/uek_release_4_packages/
    enabled = 1
    gpgcheck = 0
    exclude=postgresql*

    # vi ol7_9_latest.repo
    [ol7_9_latest]
    name = ol7_9_latest
    baseurl = http://999.999.999.999:8081/repository/latest_packages/
    enabled = 1
    gpgcheck = 0
    exclude=postgresql*

    # vi ol7_9_epel.repo
    [ol7_9_epel]
    name = ol7_9_epel
    baseurl = http://999.999.999.999:8081/repository/latest_epel_packages/
    enabled = 1
    gpgcheck = 0
    exclude=postgresql*
