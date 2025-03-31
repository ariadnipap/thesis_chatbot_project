# Grafana Upgrade

## Description
This procedure outlines the steps for upgrading Grafana on PR and DR edge nodes, ensuring minimal downtime and maintaining backup integrity.

## Prerequisites
- Access to PR and DR edge nodes:
  - pr1edge01
  - pr1edge02
  - dr1edge01
  - dr1edge02
- Grafana admin credentials
- Root access to all nodes
- Backup of installed plugins, INI file, datasources, and dashboards

## Procedure Steps

### 1. Notify Monitoring Team
Inform the monitoring team about the scheduled downtime.

### 2. Login to Edge Nodes

ssh Exxxx@XXXedgeXX sudo -i


### 3. Backup Existing Configuration
#### Backup Plugins and INI File (pr1edge01)

tar -zcvf grafana_plugins_edge01.tar.gz /var/lib/grafana/plugins tar -zcvf grafana_ini_edge01.tar.gz /etc/grafana/grafana.ini


#### Backup Grafana Datasources and Dashboards

curl -H "Authorization: Bearer <insert token>" https://<grafana host>:3000/api/datasources > grafana_datasources.json curl -H "Authorization: Bearer <insert token>" https://<grafana host>:3000/api/search | grep -o -E '"uid":"[a-zA-Z0-9_-]+"' | sed 's/"uid":"//g' | sed 's/"//g' > grafana_dashboards_uids for uid in cat grafana_dashboards_uids; do curl -H "Authorization: Bearer <insert token>" https://<grafana host>:3000/api/dashboards/uid/${uid}; done > /tmp/grafana_dashboard_${uid}.json


### 4. Setup Repositories (pr1node01)

ssh Exxxx@pr1node01 sudo -i mkdir -p /var/www/grafana8/Packages/


Move downloaded RPMs to `/var/www/html/grafana8/Packages` and create/update repository:

cd /var/www/grafana8 createrepo . createrepo --update .


### 5. Configure Repository on Edge Nodes

ssh Exxx@XXXedgeXX sudo -i vi /etc/yum.repos.d/grafana8.repo

**Add the following content:**

[grafana8] name = Grafana8 baseurl = http://pr1node01.mno.gr/grafana8/ enabled = 1 gpgcheck = 0

Copy repository file to other nodes:

scp /etc/yum.repos.d/grafana8.repo repo XXXedgeXX:/etc/yum.repos.d/


### 6. Execute Grafana Upgrade

ssh Exxx@XXXedgeXX sudo -i systemctl stop grafana-server systemctl status grafana-server yum clean all yum update grafana systemctl start grafana-server systemctl status grafana-server


Verify configurations:

sdiff /etc/grafana/grafana.ini <path/to/old/grafana.ini>


### 7. Rollback Procedure

ssh Exxx@XXXedgeXX sudo -i systemctl stop grafana-server systemctl status grafana-server yum clean all yum downgrade grafana


Restore plugins and INI file:

tar -zxvf grafana_plugins_edge0X.tar.gz -C /var/lib/grafana/plugins tar -zxvf grafana_ini_edge0X.tar.gz -C /etc/grafana/


Restart Grafana:

systemctl start grafana-server systemctl status grafana-server


## Actions Taken / Expected Output
- Grafana successfully upgraded with all dashboards and configurations intact.
- Verification through `diff` and UI checks.

## Notes and Warnings
> Ensure all backups are completed before upgrading. Downtime is expected during the upgrade.

## Affected Systems / Scope
- Grafana monitoring on PR and DR edge nodes.

## Troubleshooting / Error Handling
- **Service Not Starting:**  

journalctl -xe -u grafana-server

- **Check Logs:**  

tail -f /var/log/grafana/grafana.log


## References
- [Grafana Downloads](https://grafana.com/grafana/download?edition=oss)
- [Grafana API Documentation](https://grafana.com/docs/grafana/latest/http_api/)
