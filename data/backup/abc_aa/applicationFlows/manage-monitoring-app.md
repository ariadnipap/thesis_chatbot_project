# Monitoring application
[[_TOC_]]

## Scope
The purpose of application is to monitor all streamming and batch jobs through HTTP calls. Requests are written to database ``monitoring`` and table ``jobstatus``. Metrics about application performance are written to Graphite.

## Setup
### App
Deployed on nodes **un5**, **un6**  
- Host: `un5.bigdata.abc.gr`, `un6.bigdata.abc.gr`
- Port: 12800

Reached via HAProxy  
- Host: **un-vip.bigdata.abc.gr**
- Port: 12800

### Config Dir
 `/opt/monitoring_app/monitoring_config`


### Logs
- application logs: `/opt/monitoring-app/logs/monitoring-api.log`
  - older logs: `/opt/monitoring-app/logs/2022-11`
- access logs:  `/opt/monitoring-app/logs/tomcat/access_log.log`

### MySQL
- Host: db-vip.bigdata.abc.gr:3306
- User: monitoring
- Schema: monitoring
- Table: jobstatus

### Graphite:
- Host: un-vip.bigdata.abc.gr
- Port: 2004

## Procedure

### Check service status

#### Container
| Description| Command |
| ----------- | ----------- |
|check container is running| `sudo docker ps --filter="name=monitoring-app-{version}" --filter="status=running"`|
|check container is stopped| `sudo docker ps --filter="name=monitoring-app-{version}" --filter="status=exited"`|
|check container status| `sudo docker ps --filter="name=monitoring-app-{version}"`|
|stop monitoring-app| `sudo docker stop monitoring-app-{version}`|
|start monitoring-app|`sudo docker start monitoring-app-{version}`|
|run monitoring-app if container is killed & removed|[use start app script](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/Deployment-PROD#run-start-up-script)|

### Stop/Start procedures
#### Connect to nodes
1. SSH to un2   
`ssh root@un2`
2. SSH to un5/un6 nodes via personal sudoer user.  
(superuser privileges to perform Docker operations)
   1. `ssh <user>@<un5/un6>`
   1. `sudo su`

#### Stop current container
1. Get container name with docker ps as described above
2. Stop container  
`docker stop monitoring-app-{version}`

#### Start stopped container
To start the container using the latest version (the latest container version is the one that was stopped with the previous command) use,
`docker start monitoring-app-{version}`

#### API calls
- Using un5 IP

| Description | Command |
| ----------- | ----------- |
| Check app is running | `curl --location --request GET 'http://999.999.999.999:12800/monitoring/app/status'` |
| Check Load Balancer is enabled | `curl --location --request GET 'http://999.999.999.999:12800/monitoring/app/lb/check' `|
| Enable Load Balancer | `curl --location --request PUT 'http://999.999.999.999:12800/monitoring/app/lb/enable'` |
| Disable Load Balancer  | `curl --location --request PUT 'http://999.999.999.999:12800/monitoring/app/lb/disable'`|

### Troubleshooting Step
- Check [logs](#logs) to identify the problem 


### Deployment steps
- [Deployment guide](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/Deployment-PROD)

