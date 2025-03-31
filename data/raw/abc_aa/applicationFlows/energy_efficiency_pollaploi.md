# Energy-Efficiency Pollaploi

## Overview

This is an `Oozie Flow` responsible to **load data** from **txt files** into **impala tables**. Through the **Oozie Workflow** a **ssh** action is performed which executes the `pollaploi.sh` script. 

- **Utility Node / Server:** `un2.bigdata.abc.gr`
  - **User:** `intra`
  - [Password](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/abc/devpasswd.kdbx)
  - **Main File Directory:** `/shared/abc/energy_efficiency/load_pollaploi/`
- **Oozie Coordinator**
  - **Hue:** `https://un-vip.bigdata.abc.gr:8888`
  - **User:** `intra`
  - **Coordinator:** `coord_energy_efficiency_load_pollaploi`
    - **Execution:** 
      - **Winter time:** `every day at 21:00 local time (9PM)`
      - **Daylight saving time:** `every day at 22:00 local time (10PM)`
    - **Approximate Duration:** `8 seconds`
    - **Workflow:** `energy_efficiency_load_pollaploi`
      - **SSH Server:** `un-vip.bigdata.abc.gr`
      - **SSH User:** `intra2`
      - [Script](https://metis.ghi.com/obss/bigdata/abc/reporting/reporting/-/blob/master/FLOWS/energy_efficiency/PROD/load_pollaploi/pollaploi/pollaploi.sh)
      - **Logs:** `view through job run - NO LOGS`

## Pollaploi Flow

The `pollaploi flow` gets a .txt file from a remdef sftp directory and moves it to a temporary directory on the utility node. Then it unzips the file that was just transferred and compares it to another.txt file in the curr directory on the utility node. If those files are the same then it does nothing, since it means that the file has already been processed by the flow. If the file names are different then it removes the old file in the curr directory and moves the new file from the temp to the curr directory. After that the new file in the curr directory is put in a hdfs path. From there impala queries are executed clearing the pollaploi table, loading the data from the new file and refreshing the pollaploi table. 

- **SFTP:** 
   - **Initiator:** `intra` user
	- **User:** `bigd`
	- **Password:** `passwordless`
	- **Server:** `999.999.999.999`
	- **Path:** `/energypm/`
	- **Compressed File:** `*_pollaploi.zip` containing `*_pollaploi.txt`
- **Utility Node Directories:**
	- **Curr:** `/shared/abc/energy_efficiency/load_pollaploi/pollaploi_curr`
	- **Temp:** `/shared/abc/energy_efficiency/load_pollaploi/pollaploi_temp`
  - **Scripts:** `/shared/abc/energy_efficiency/load_pollaploi/pollaploi`
- **HDFS:**
	- **Path:** `/ez/landingzone/energy_temp/`
- **Impala:** 
	- **Database:** `energy_efficiency`
	- **Table Name:** `pollaploi`
	- **Retention:** `-`
- **Logs:**
  - **Path:** `/shared/abc/energy_efficiency/load_pollaploi/log`
  - **Retention:** `none` (since 15/12/2019)

**_Ndef:_** One of the `impala-shell` queries executed is the `LOAD DATA INPATH <hdfs_path>/<filename>` As seen in this [article](https://impala.apache.org/docs/build/html/topics/impala_load_data.html) the LOAD DATA INPATH command moves the loaded data file (not copies) into the Impala data directory. So the log entry `rm: /ez/landingzone/energy_temp/2023_03_01_pollaploi.txt': No such file or directory` is not something to worry about. 

**_[Sample data from pollaploi table](https://metis.ghi.com/obss/bigdata/abc/reporting/reporting/-/blob/master/FLOWS/energy_efficiency/TEST%20%CE%91%CE%A1%CE%A7%CE%95%CE%99%CE%91/2019_05_pollaploi.txt)_** 

## Troubleshooting Steps

Due to the occurance of these tickets (**SD2179931** and **SD2021989**) the below steps should be followed for troubleshooting.

1. Check that a new file `*pollaploi.zip` is placed in the `remdef SFTP directory`. Because the `workflow` runs in the evening (9PM or 10PM), if a file is placed earlier in the remdef SFTP directory and the client asks why it hasn't been loaded, wait until the next day and follow the steps mentioned here to see its execution.

1. Check that a file `*pollaploi.txt` exists in `/shared/abc/energy_efficiency/load_pollaploi/pollaploi_curr`.

1. Based on the `date` the file has in `/shared/abc/energy_efficiency/load_pollaploi/pollaploi_curr` check the log file `pollaploi.<YYYYMMDD>.log` of that specific day. E.g. 

    ```
    $ ls -l /shared/abc/energy_efficiency/load_pollaploi/pollaploi_curr/
    > -rw-r--r-- 1 intra intra 1034132960 Mar 22 18:34 2023_03_01_pollaploi.txt
    $ less /shared/abc/energy_efficiency/load_pollaploi/log/pollaploi.20230322.log
    ```
1. In `Hue` go to `Jobs` and search `energy` in the search bar. View the last executed `workflow` and see if it has run successfully.   

### Possible Response to Ticket

**_Ticket:_**
``` 
Good morning,
the new pollaploi file has been uploaded but the corresponding table has not been updated yet
Thank you.
```

**_Response:_** (example)
```
Good evening.
There seems to be no new file in the sftp directory /energypm. The workflow that loads the table runs every day at 9PM/10PM, so if a file is added today it will be loaded in the evening. The last file that has been loaded is named 2023_03_01_pollaploi and from the logs on 2023-03-22 it seems to have been loaded normally.
```
## Useful Links

- **[GitLab Repo](https://metis.ghi.com/obss/bigdata/abc/reporting/reporting/-/tree/master/FLOWS/energy_efficiency)**

