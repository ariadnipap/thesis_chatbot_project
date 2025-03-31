# Monitoring Application

## 1. Overview

The purpose of the application is to monitor all streaming and batch jobs through HTTP calls. Requests are written to the database `monitoring` and table `jobstatus`. Metrics about application performance are written to Graphite.

---

## 2. Installation & Configuration

### App Deployment
- **Nodes**: `un5`, `un6`
- **Host**: `un5.bigdata.abc.gr`, `un6.bigdata.abc.gr`
- **Port**: `12800`
- **HAProxy**: `un-vip.bigdata.abc.gr:12800`

### Configuration Directory
- **Path**: `/opt/monitoring_app/monitoring_config`

### Logs
- **Application Logs**: `/opt/monitoring-app/logs/monitoring-api.log`
- **Older Logs**: `/opt/monitoring-app/logs/2022-11`
- **Access Logs**: `/opt/monitoring-app/logs/tomcat/access_log.log`

### MySQL Database
- **Host**: `db-vip.bigdata.abc.gr:3306`
- **User**: `monitoring`
- **Schema**: `monitoring`
- **Table**: `jobstatus`

### Graphite
- **Host**: `un-vip.bigdata.abc.gr`
- **Port**: `2004`

---

## 3. Data Processing

### Check Service Status

#### Container Management Commands

| Description | Command |
| ----------- | ----------- |
| Check if container is running | `sudo docker ps --filter="name=monitoring-app-{version}" --filter="status=running"` |
| Check if container is stopped | `sudo docker ps --filter="name=monitoring-app-{version}" --filter="status=exited"` |
| Check container status | `sudo docker ps --filter="name=monitoring-app-{version}"` |
| Stop monitoring-app | `sudo docker stop monitoring-app-{version}` |
| Start monitoring-app | `sudo docker start monitoring-app-{version}` |
| Run monitoring-app if container is killed & removed | [Start app script](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/Deployment-PROD#run-start-up-script) |

---

## 4. Monitoring & Debugging

### Stop/Start Procedures

#### Connect to Nodes
1. SSH to `un2`  
   ```bash
   ssh root@un2
   ```
2. SSH to `un5` or `un6` via a personal sudoer user:
   ```bash
   ssh <user>@<un5/un6>
   sudo su
   ```

#### Stop Current Container
1. Get the container name using:
   ```bash
   sudo docker ps --filter="name=monitoring-app-{version}"
   ```
2. Stop the container:
   ```bash
   docker stop monitoring-app-{version}
   ```

#### Start Stopped Container
To start the container using the latest version (which was previously stopped), run:
```bash
docker start monitoring-app-{version}
```

### API Calls for Service Checks

| Description | Command |
| ----------- | ----------- |
| Check app is running | `curl --location --request GET 'http://999.999.999.999:12800/monitoring/app/status'` |
| Check Load Balancer is enabled | `curl --location --request GET 'http://999.999.999.999:12800/monitoring/app/lb/check'` |
| Enable Load Balancer | `curl --location --request PUT 'http://999.999.999.999:12800/monitoring/app/lb/enable'` |
| Disable Load Balancer  | `curl --location --request PUT 'http://999.999.999.999:12800/monitoring/app/lb/disable'` |

---

## 5. Troubleshooting

### Steps to Identify Issues
- Check [logs](#logs) for error messages.
- Ensure the container is running using:
  ```bash
  sudo docker ps --filter="name=monitoring-app-{version}"
  ```
- If the container is not running, restart it:
  ```bash
  docker start monitoring-app-{version}
  ```

---

## 6. Data Validation & Checks

- Verify monitoring database connectivity:
  ```bash
  mysql -umonitoring -p -h db-vip.bigdata.abc.gr
  use monitoring;
  select * from jobstatus limit 10;
  ```
- Check Graphite metrics to ensure data is being recorded.

---

## 7. Miscellaneous Notes

### Deployment Steps
- [Deployment Guide](https://metis.ghi.com/obss/bigdata/common-dev/apps/monitoring/monitoring-devops/-/wikis/Deployment-PROD)

---

