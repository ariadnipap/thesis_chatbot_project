# Nagios Alarms & Errors Resolution

## Description
This procedure outlines the steps required to resolve errors appearing in Nagios, including:
- `/etc/bashrc: fork: retry: Resource temporarily unavailable`
- `ssh_exchange_identification: Connection closed by remdef host`
- `Return code of 255 is out of bounds`

## Prerequisites
- SSH access to the Nagios admin node with root privileges.
- Permission to modify Nagios configuration files.
- Ability to restart the Nagios service.

## Affected Systems / Scope
- **Nagios Monitoring System**
- **BigStreamer Infrastructure**
- **Nagios Configuration Files:**
  - `/home/nagios/.bashrc`
  - `/usr/local/nagios/etc/objects/commands.cfg`
  - `/usr/local/nagios/etc/nagios.cfg`

## Procedure Steps

### **1. Fix "fork" Error**
1. **SSH into the Nagios Admin Node as Root**
   ```bash
   ssh root@nagios-admin
   ```

2. **Modify the `.bashrc` File for the Nagios User**
   ```bash
   vi /home/nagios/.bashrc
   ```
   - Add the following lines:
     ```bash
     ulimit -u 8888
     ulimit -n 2222
     ```
   - Save and exit.

---

### **2. Fix "ssh_exchange_identification: Connection closed by remdef host" Error**
1. **Edit the `commands.cfg` Configuration File**
   ```bash
   vi /usr/local/nagios/etc/objects/commands.cfg
   ```
2. **Modify the following line:**
   ```bash
   $USER1$/check_by_ssh  -H $HOSTADDRESS$ -t 30 -C "/usr/lib/nagios/plugins/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$"
   ```
   - Replace it with:
     ```bash
     $USER1$/check_by_ssh -E 8 -o StrictHostKeyChecking=no -H $HOSTADDRESS$ -t 30 -C "/usr/lib/nagios/plugins/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$"
     ```
3. **Save the file and exit.**

---

### **3. Fix "Return code of 255 is out of bounds" Error**
1. **Edit the `nagios.cfg` Configuration File**
   ```bash
   vi /usr/local/nagios/etc/nagios.cfg
   ```
2. **Modify the `max_concurrent_checks` Parameter**
   - Locate the line:
     ```bash
     max_concurrent_checks=0
     ```
   - Change the value to:
     ```bash
     max_concurrent_checks=50
     ```
3. **Save the file and exit.**
4. **Restart the Nagios Service**
   ```bash
   service nagios restart
   ```

---

## Actions Taken / Expected Output
- **Fork error fixed:** `ulimit` values increased for Nagios user.
- **SSH connection error resolved:** Command modified to disable strict host key checking.
- **Return code error eliminated:** `max_concurrent_checks` adjusted and Nagios restarted.

## Notes and Warnings
> Ensure Nagios configurations are backed up before making changes.  
> Restarting Nagios may cause temporary monitoring disruptions.

## Troubleshooting / Error Handling
- **If Nagios fails to restart, check logs:**
  ```bash
  tail -f /var/log/nagios/nagios.log
  ```
- **Verify that changes are applied:**
  ```bash
  cat /home/nagios/.bashrc
  grep 'max_concurrent_checks' /usr/local/nagios/etc/nagios.cfg
  ```

## References
