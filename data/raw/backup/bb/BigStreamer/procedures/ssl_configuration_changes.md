# SSL Configuration Changes

## Description
This procedure describes the necessary **SSL configuration changes** for **httpd, nginx, haproxy, and sshd** services on PR and DR edge nodes. The updates **improve security** by enforcing **TLSv1.2** and strengthening cryptographic settings.

### **Affected Edge Nodes**
- `pr1edge01`
- `pr1edge02`
- `dr1edge01`
- `dr1edge02`

---

## Prerequisites
- **Administrator access** to edge nodes.
- **SSH access** to each node.
- **Cluster resource switchover procedures** should be followed before making changes.
- **Backup of configuration files** before modifications.

---

## Procedure Steps

### **1. Preparation**
1. **SSH into the edge node**:
   ```bash
   ssh Exxxx@XXXedgeXX
   sudo -i
   ```

2. **Switchover cluster resources** (if required) before applying changes.
   > Follow the procedures described in the **Switchover of Cluster Resources** chapter  
   > **Security Vulnerabilities MOP**:  
   > [Click here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)

---

### **2. httpd Configuration Changes**
1. **Backup existing httpd configuration files**:
   ```bash
   cp -ap /etc/httpd/conf.d/ssl.conf "/etc/httpd/conf.d/ssl.conf.bak.$(date +%Y%m%d)"
   cp -ap /etc/httpd/conf/httpd.conf "/etc/httpd/conf/httpd.conf.bak.$(date +%Y%m%d)"
   cp -ap /etc/httpd/conf.d/graphite-web.conf "/etc/httpd/conf.d/graphite-web.conf.bak.$(date +%Y%m%d)"
   ```

2. **Modify `/etc/httpd/conf/httpd.conf`**:
   - Add:
     ```bash
     TraceEnable Off
     ```
   - Add to `/etc/httpd/conf/httpd.conf`, `/etc/httpd/conf.d/ssl.conf`, and `/etc/httpd/conf.d/graphite-web.conf`:
     ```bash
     SSLProtocol +TLSv1.2
     ```
   - Remove the following lines:
     ```bash
     SSLHonorCipherOrder Off
     SSLCipherSuite ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES256:ECDH+AES128:!aNULL:!SHA1:!AESCCM:!MD5:!3DES:!DES:!IDEA
     ```

3. **Restart httpd service**:
   ```bash
   systemctl restart httpd
   ```

---

### **3. nginx Configuration Changes**
1. **Backup existing nginx configuration**:
   ```bash
   cp -ap /etc/nginx/nginx.conf "/etc/nginx/nginx.conf.bak.$(date +%Y%m%d)"
   ```

2. **Modify `/etc/nginx/nginx.conf`**:
   - Add:
     ```bash
     ssl_protocols TLSv1.2;
     ```

3. **Disable and restart nginx service**:
   ```bash
   systemctl disable --now nginx
   systemctl start nginx
   ```

---

### **4. haproxy Configuration Changes**
1. **Backup existing haproxy configuration**:
   ```bash
   cp -ap /etc/haproxy/haproxy.cfg "/etc/haproxy/haproxy.cfg.bak.$(date +%Y%m%d)"
   ```

2. **Modify haproxy configuration**:
   - Add the following options for **ports 8889 and 25002**, repeating the same for `hue_vip`:
     ```bash
     bind 999.999.999.999:25002 ssl crt no-sslv3 /opt/haproxy/security/x509/node.haproxy.pem
     ```

3. **Restart haproxy service**:
   ```bash
   systemctl restart haproxy
   ```

---

### **5. sshd Configuration Changes**
1. **Backup existing sshd configuration**:
   ```bash
   cp -ap /etc/ssh/sshd_config "/etc/ssh/sshd_config.bak.$(date +%Y%m%d)"
   ```

2. **Modify `/etc/ssh/sshd_config`**:
   - Add the following security settings:
     ```bash
     Ciphers aes256-ctr,aes192-ctr,aes128-ctr # 5.2.11
     KexAlgorithms ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha256
     ```

3. **Restart sshd service**:
   ```bash
   systemctl restart sshd
   ```

---

## Actions Taken / Expected Output
- **SSL settings updated** for `httpd`, `nginx`, `haproxy`, and `sshd`.
- **TLSv1.2 enforced** on all relevant services.
- **Configuration files backed up** before modification.
- **Services restarted successfully** without errors.

### **Verification**
To confirm that the changes are applied correctly:

1. **Check httpd SSL configuration**:
   ```bash
   grep "SSLProtocol" /etc/httpd/conf.d/ssl.conf
   ```

2. **Verify nginx SSL configuration**:
   ```bash
   grep "ssl_protocols" /etc/nginx/nginx.conf
   ```

3. **Confirm haproxy binding**:
   ```bash
   netstat -tulnp | grep haproxy
   ```

4. **Check SSH cipher settings**:
   ```bash
   ssh -Q cipher
   ```

> **Expected Output:** TLSv1.2 should be enabled, haproxy should bind to the correct ports, and SSH should list only the specified ciphers.

---

## Notes and Warnings
> - **Ensure that backups are taken** before making changes.
> - **Only restart services during a maintenance window** to avoid disruptions.
> - **Double-check haproxy and sshd configurations** before restarting.
> - If nginx is disabled, ensure that it is **intentionally stopped** and does not need to be restarted.

---

## Affected Systems / Scope
- **PR and DR Edge Nodes**
- **httpd, nginx, haproxy, and sshd services**
- **Applications relying on these services for SSL/TLS communication**

---

## Troubleshooting / Error Handling

### **Common Issues & Solutions**
- **Issue:** httpd fails to restart.  
  **Solution:** Check for syntax errors:
  ```bash
  apachectl configtest
  ```

- **Issue:** nginx does not start.  
  **Solution:** Verify the configuration:
  ```bash
  nginx -t
  ```

- **Issue:** haproxy does not bind to ports.  
  **Solution:** Confirm that no other process is using the ports:
  ```bash
  netstat -tulnp | grep 25002
  ```

- **Issue:** SSH does not accept connections after restart.  
  **Solution:** Restore the backup configuration and restart sshd:
  ```bash
  cp /etc/ssh/sshd_config.bak.$(date +%Y%m%d) /etc/ssh/sshd_config
  systemctl restart sshd
  ```

### **Log File Locations**
```bash
tail -f /var/log/httpd/error_log
tail -f /var/log/nginx/error.log
tail -f /var/log/haproxy.log
tail -f /var/log/secure
```

---

## References
- [Security Vulnerabilities MOP](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx)
- [Apache httpd Documentation](https://httpd.apache.org/docs/)
- [nginx SSL Configuration Guide](https://nginx.org/en/docs/)
- [haproxy Configuration Guide](http://www.haproxy.org/)
- [OpenSSH Hardening](https://www.ssh.com/academy/ssh/hardening)

