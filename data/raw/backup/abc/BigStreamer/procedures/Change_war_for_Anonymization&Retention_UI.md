# Permanent Anonymization & Retention UI Issue

## Description
Regarding the issue with the UI of Permanent Anonymization & Retention (`https://cne.def.gr:8643/customapps`).  
Note that access to this UI is not possible via VPN.  
The reason is that it attempts to load a library from the internet (`cdn.jsdelivr.net`).  
A new WAR file has been added, which needs to replace the old one in WildFly.

## Prerequisites
- SSH access to `unc2`, `unekl1`, and `unekl2` servers.
- The new WAR file must be available before replacing the old one.

## Procedure Steps

1. **Connect to the server**
   - SSH using your personal account:
     ```bash
     ssh user@unc2
     ```

2. **Check HAProxy Configuration**
   - Gain root privileges:
     ```bash
     sudo -i
     ```
   - Open the HAProxy configuration file:
     ```bash
     less /etc/haproxy/haproxy.cfg
     ```
   - Search for the backend:
     ```
     tru-backend
     ```

3. **Backup the old WAR file**
   - SSH into `unekl1`:
     ```bash
     ssh user@unekl1
     ```
   - Create a backup of the WAR file:
     ```bash
     cp -rp /opt/trustcenter/wf_cdef_trc/standalone/deployments/wftrust-landing-web.war /opt/trustcenter/wf_cdef_trc/standalone/wftrust-landing-web.war.bkp
     ```

4. **Replace the WAR file**
   - Set the correct ownership and permissions:
     ```bash
     chown trustuser:trustcenter <new_war_file>
     chmod 644 <new_war_file>
     ```
   - Move the new WAR file into place:
     ```bash
     mv <new_war_file> /opt/trustcenter/wf_cdef_trc/standalone/deployments/
     ```

5. **Verify deployment**
   - Restarting WildFly is **not necessary**. A new `wftrust-landing-web.war.deployed` file will be created automatically.

6. **Check WildFly status**
   - Switch to the `trustuser` account:
     ```bash
     su - trustuser
     bash
     ```
   - Verify that WildFly is running:
     ```bash
     trust-status
     ```

7. **Apply changes to `unekl2`**
   - Perform the same WAR replacement steps on `unekl2`.

8. **Clear cache and test the UI**
   - Clear your browser cache and try accessing:
     ```
     https://cne.def.gr:8643/customapps
     ```

## Actions Taken / Expected Output
- The new WAR file should be deployed successfully.
- WildFly should automatically detect and deploy the new file.
- The UI should be accessible without requiring VPN.

## Notes and Warnings
> Restarting WildFly is **not necessary**; deployment happens automatically.

## Affected Systems / Scope
- **abc Bigstreamer**

## Troubleshooting / Error Handling
- If the UI is still inaccessible, verify that the new WAR file has been correctly deployed.
- Check WildFly logs for deployment issues:
  ```bash
  tail -f /opt/trustcenter/wf_cdef_trc/standalone/log/server.log
  ```
- Verify HAProxy backend settings:
  ```bash
  cat /etc/haproxy/haproxy.cfg | grep tru-backend
  ```

## References

