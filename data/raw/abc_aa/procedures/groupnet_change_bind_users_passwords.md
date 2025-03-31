# GROUPNET - Change bind users' passwords

- [GROUPNET - Change bind users' passwords](#groupnet---change-bind-users-passwords)
  - [RAN.AI Geolocation - t1-svc-cneranaibind](#ranai-geolocation---t1-svc-cneranaibind)
  - [R-Studio Connect - t1-svc-cnebind](#r-studio-connect---t1-svc-cnebind)
    - [Re-activate License for R-Studio Connect](#re-activate-license-for-r-studio-connect)

The purpose of this document is to describe the procedure on how to change the passwords for the bind users used for querying the LDAP of GROUPNET domain.

## RAN.AI Geolocation - t1-svc-cneranaibind

1. Inform users that the authentication with GROUPNET accounts may encounter errors during the procedure (approximate 1 hour). No pod will be restarted.
2. Go to [https://cne.def.gr/auth/admin](https://cne.def.gr/auth/admin)
3. Login with an administrative account
4. Navigate to User Federation > GROUPNET
5. Request password update `t1-svc-cneranaibind` via Remedy and obtain the new password
6. Update `Bind Credential` field and press `Save`
7. Press `Test authentication`

## R-Studio Connect - t1-svc-cnebind

1. Inform users for downtime of approximate 1 hour
2. Login to `unrstudio1.bigdata.abc.gr` as root via Cyberark
3. Request password update `t1-svc-cnebind` via Remedy and obtain the new password
4. Edit `/etc/rstudio-connect/rstudio-connect.gcfg`

    ``` bash
    vi  /etc/rstudio-connect/rstudio-connect.gcfg
    # Update **BindPassword** with the password obtained in step 3 and save
    ```

5. Restart R-Studio Connect

    ``` bash
    systemctl restart rstudio-connect
    ```

6. Check R-Studio Connect status

    ``` bash
    systemctl status rstudio-connect
    ```

7. Verify LDAP authentication by logging in to [https://unrstudio1.bigdata.abc.gr/connect](https://unrstudio1.bigdata.abc.gr/connect)
8. Due to the fact that the server is not directly connected to the Internet, R-Studio Connect might display an error about expired license after the reboot. In this case follow the steps listed [below](#re-activate-license-for-r-studio-connect).
9. Inform users that the application is available.

### Re-activate License for R-Studio Connect

1. Login to `unrstudio1.bigdata.abc.gr` as root via Cyberark
2. Ensure that time is accurate and the time zone is correct for the machine.

    ```bash
    timedatectl
    ```

3. Sync date and time to hardware clock of the machine.

    ``` bash
    hwclock -w
    ```

4. Deactivate license

    ``` bash
    export http_proxy=http://un-vip.bigdata.abc.gr:5555
    export https_proxy=http://un-vip.bigdata.abc.gr:5555
    /opt/rstudio-connect/bin/license-manager deactivate
    ```

5. Activate license

    ``` bash
    export http_proxy=http://un-vip.bigdata.abc.gr:5555
    export https_proxy=http://un-vip.bigdata.abc.gr:5555
    /opt/rstudio-connect/bin/license-manager activate <product-key>
    # This should display Activation status as Activated 
    ```

6. In case you  receive the following

   ``` text
   Error activating product key: (13): The activation has expired or the system time has been tampered with. Ensure your time, timezone, and date settings are correct. If you're sure the license is not expired, try performing the following steps, in order: 
   1. Fix the timezone on your system.
   2. Fix the date on your system.
   3. Fix the time on your system.
   4. Perform a system restart (important!)
   ```

   Fix any time/date issues and **reboot the server**.

7. Verify license status

    ``` bash
    /opt/rstudio-connect/bin/license-manager status
    /opt/rstudio-connect/bin/license-manager verify
    ```

8. Restart R-Studio Connect

    ``` bash
    systemctl restart rstudio-connect
    ```

9. Check R-Studio Connect status

    ``` bash
    systemctl status rstudio-connect
    ```

10. Verify LDAP authentication by logging in to [https://unrstudio1.bigdata.abc.gr/connect](https://unrstudio1.bigdata.abc.gr/connect)
