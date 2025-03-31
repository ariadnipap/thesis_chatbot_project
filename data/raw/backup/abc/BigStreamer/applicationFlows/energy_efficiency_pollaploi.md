# Energy-Efficiency Pollaploi

## 1. Overview

The **Energy-Efficiency Pollaploi** flow is an **Oozie Workflow** responsible for **loading data** from `.txt` files into **Impala tables**. The process is executed via an **SSH action**, which runs the `pollaploi.sh` script.

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

## 2. Installation & Configuration

### 2.1. Scripts & Configuration

#### Install Dependencies
- Ensure access to the **utility node** `un2.bigdata.abc.gr` under the `intra` user.
- Validate SSH connectivity and key-based authentication for script execution.

#### Configure Oozie
- Verify the **Oozie Coordinator** settings for scheduled execution at **21:00 (Winter)** and **22:00 (DST)**.
- Confirm proper integration with the `pollaploi.sh` script and **SSH execution permissions**.

## 3. Data Processing

### Pollaploi Flow

The **Pollaploi Flow** retrieves `.txt` files from an **SFTP directory** and processes them through multiple steps:

1. **Retrieve and Compare Files**  
   - Download the `.zip` file from **SFTP**.
   - Extract the `.txt` file and compare it to the current file in the **utility node**.
   - If the file is identical, **no action is taken**.

2. **Move and Store Data**  
   - Replace the old file in `/pollaploi_curr/` with the new one.
   - Transfer the new file to **HDFS** (`/ez/landingzone/energy_temp/`).

3. **Load Data into Impala**  
   - Clear the **pollaploi** table.
   - Load new data using `LOAD DATA INPATH <hdfs_path>/<filename>`.
   - Refresh Impala metadata.

### File Paths and Configurations

#### **SFTP Configuration**
- **Initiator:** `intra`
- **SFTP User:** `bigd`
- **Server:** `999.999.999.999`
- **File Path:** `/energypm/`
- **Compressed File Format:** `*_pollaploi.zip`
- **Extracted File Format:** `*_pollaploi.txt`

#### **Utility Node Directories**
- **Current Files:** `/shared/abc/energy_efficiency/load_pollaploi/pollaploi_curr`
- **Temporary Files:** `/shared/abc/energy_efficiency/load_pollaploi/pollaploi_temp`
- **Scripts Directory:** `/shared/abc/energy_efficiency/load_pollaploi/pollaploi`

#### **HDFS Storage**
- **Path:** `/ez/landingzone/energy_temp/`

#### **Impala Database Configuration**
- **Database:** `energy_efficiency`
- **Table Name:** `pollaploi`

**Note:**  
- **Logs are not retained** since `15/12/2019`.
- The **`LOAD DATA INPATH` command moves files** into the Impala directory, causing `rm` errors (`No such file or directory`). This is expected behavior.


## 4. Monitoring & Debugging

### 4.1. Logs
- **Log Path:** `/shared/abc/energy_efficiency/load_pollaploi/log`
- **Retrieve logs:**
  ls -l /shared/abc/energy_efficiency/load_pollaploi/log

    Example log check:

    less /shared/abc/energy_efficiency/load_pollaploi/log/pollaploi.20230322.log

### 4.2. Monitoring Steps

    Check SFTP Directory

ssh intra@un2.bigdata.abc.gr
ls -l /energypm/

Check Current File Directory

ls -l /shared/abc/energy_efficiency/load_pollaploi/pollaploi_curr/

Check Oozie Execution

    Login to Hue (https://un-vip.bigdata.abc.gr:8888).
    Navigate to Jobs > energy_efficiency_load_pollaploi.
    Verify last execution status.

Impala Table Data Check

    impala-shell -i un-vip.bigdata.abc.gr -d energy_efficiency --ssl -k -q "SELECT * FROM pollaploi LIMIT 3;"

## 5. Troubleshooting
### 5.1. Common Errors & Fixes
Issue	Cause	Solution
File not found in SFTP	Delay in file upload	Wait until next run, check manually
No new data in Impala	Old file detected, not reloaded	Verify /pollaploi_curr/, delete old file
rm: No such file or directory	Expected behavior (LOAD DATA INPATH)	Ignore the error

### 5.2. Example Ticket & Response
Ticket

Καλημέρα σας ,
έχει ανέβει το νέο αρχείο pollaploi αλλά ο αντίστοιχος πίνακας δεν έχει ενημερωθεί ακόμα.
Σας ευχαριστώ.

Response

Καλησπέρα.
Φαίνεται να μην υπάρχει νέο αρχείο στο SFTP directory /energypm. 
Το workflow που φορτώνει τον πίνακα τρέχει κάθε μέρα στις 9PM/10PM, 
οπότε εάν μπει αρχείο σήμερα θα το φορτώσει το βράδυ.
Το τελευταίο αρχείο που έχει φορτωθεί έχει όνομα 2023_03_01_pollaploi 
και από τα logs στις 2023-03-22 φαίνεται να έχει φορτωθεί κανονικά.

## 6. Data Validation & Checks

    Check Impala table consistency:

impala-shell -i un-vip.bigdata.abc.gr -d energy_efficiency --ssl -k -q "SELECT COUNT(*) FROM pollaploi;"

Validate last execution logs:

less /shared/abc/energy_efficiency/load_pollaploi/log/pollaploi.<YYYYMMDD>.log

Ensure correct file movement in HDFS:

    hdfs dfs -ls /ez/landingzone/energy_temp/

## 7. Miscellaneous Notes

    Execution runs once daily (21:00 Winter / 22:00 DST).
    No log retention policy since 15/12/2019.
    Impala LOAD DATA moves files, which may cause expected errors.
    Hue monitoring is the primary method to check execution status.

## 8. Useful Links

https://metis.ghi.com/obss/bigdata/abc/reporting/reporting/-/tree
