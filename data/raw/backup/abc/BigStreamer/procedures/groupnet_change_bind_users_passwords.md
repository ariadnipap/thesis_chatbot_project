# GROUPNET - Change Bind Users' Passwords

## Description
This procedure outlines the steps to change the passwords for bind users used for querying the LDAP of the GROUPNET domain.

## Prerequisites
- Access to the GROUPNET authentication management portal.
- Administrative account credentials for authentication.
- Access to `unrstudio1.bigdata.abc.gr` as `root` via Cyberark.
- Permission to modify LDAP settings.
- Knowledge of the new passwords obtained via Remedy.

## Procedure Steps

### **1. Change Password for RAN.AI Geolocation - `t1-svc-cneranaibind`**
1. Inform users that authentication with GROUPNET accounts may experience issues during the procedure (approx. **1 hour**). No pods will be restarted.
2. Navigate to the GROUPNET authentication management portal:
   ```
   https://cne.def.gr/auth/admin
   ```
3. Login with an administrative account.
4. Navigate to **User Federation > GROUPNET**.
5. Request a password update for `t1-svc-cneranaibind` via Remedy and obtain the new password.
6. Update the `Bind Credential` field and press **Save**.
7. Press **Test Authentication** to verify changes.

---

### **2. Change Password for R-Studio Connect - `t1-svc-cnebind`**
1. Inform users about the expected downtime of approximately **1 hour**.
2. Login to `unrstudio1.bigdata.abc.gr` as `root` via Cyberark.
3. Request a password update for `t1-svc-cnebind` via Remedy and obtain the new password.
4. Edit the R-Studio Connect configuration file:
   ```bash
   vi /etc/rstudio-connect/rstudio-connect.gcfg
   ```
   - Update the `BindPassword` field with the new password.
   - Save and exit the file.
5. Restart R-Studio Connect:
   ```bash
   systemctl restart rstudio-connect
   ```
6. Check the status of R-Studio Connect:
   ```bash
   systemctl status rstudio-connect
   ```
7. Verify LDAP authentication by logging in to:
   ```
   https://unrstudio1.bigdata.abc.gr/connect
   ```
8. If the server is not connected to the internet, R-Studio Connect may show an expired license error. Follow the re-activation steps below.
9. Inform users that the application is available.

---

### **3. Re-Activate License for R-Studio Connect**
1. Login to `unrstudio1.bigdata.abc.gr` as `root` via Cyberark.
2. Ensure that the system time and timezone are correct:
   ```bash
   timedatectl
   ```
3. Sync the date and time with the hardware clock:
   ```bash
   hwclock -w
   ```
4. Deactivate the license:
   ```bash
   export http_proxy=http://un-vip.bigdata.abc.gr:5555
   export https_proxy=http://un-vip.bigdata.abc.gr:5555
   /opt/rstudio-connect/bin/license-manager deactivate
   ```
5. Activate the license:
   ```bash
   export http_proxy=http://un-vip.bigdata.abc.gr:5555
   export https_proxy=http://un-vip.bigdata.abc.gr:5555
   /opt/rstudio-connect/bin/license-manager activate <product-key>
   ```
   - The output should display **Activation status as Activated**.
6. If you receive the following error:
   ```
   Error activating product key: (13): The activation has expired or the system time has been tampered with.
   ```
   - Fix any time/date issues.
   - **Reboot the server**.
7. Verify the license status:
   ```bash
   /opt/rstudio-connect/bin/license-manager status
   /opt/rstudio-connect/bin/license-manager verify
   ```
8. Restart R-Studio Connect:
   ```bash
   systemctl restart rstudio-connect
   ```
9. Check the status of R-Studio Connect:
   ```bash
   systemctl status rstudio-connect
   ```
10. Verify LDAP authentication by logging in to:
    ```
    https://unrstudio1.bigdata.abc.gr/connect
    ```

## Actions Taken / Expected Output
- The bind user passwords are updated successfully.
- LDAP authentication works without issues.
- R-Studio Connect runs with the new credentials.
- If needed, the R-Studio Connect license is reactivated.

## Notes and Warnings
> Users may experience temporary authentication issues during the process.  
> Ensure the correct password is obtained and applied in all necessary locations.

## Affected Systems / Scope
- GROUPNET LDAP authentication.
- RAN.AI Geolocation.
- R-Studio Connect.

## Troubleshooting / Error Handling
- If LDAP authentication fails, verify the bind credentials and re-enter the password.
- Check the R-Studio Connect logs for errors:
  ```bash
  tail -f /var/log/rstudio-connect.log
  ```
- If the license activation fails, ensure system time is synchronized.

## References
- [GROUPNET Authentication Management Portal](https://cne.def.gr/auth/admin)

