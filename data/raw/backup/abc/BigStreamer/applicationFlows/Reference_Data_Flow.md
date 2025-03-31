# Reference Data Flow

## 1. Overview

The **Reference Data Flow** is responsible for loading **Reference Data flat files** into **Hive tables** and maintaining a **historical record**. The process runs **daily at 00:05 UTC** and consists of **two scripts**:
- `210_refData_Load.sh`: Reads, parses, and loads reference files into **LOAD tables**.
- `220_refData_Daily_Snapshot.sh`: Extracts the latest **snapshot** from LOAD tables.

---

## 2. Installation & Configuration

### Data Source File
- **Host**: `un2.bigdata.abc.gr (999.999.999.999)`
- **User**: `vantagerd`
- **Spool Area**: `/data/1/vantage_ref-data/REF-DATA/` (linked to `/shared/vantage_ref-data/REF-DATA`)
- **File Format**: `<refType>_<refDate>.csv.gz`
  - `<refType>`: `cells, crm, devices, services`
  - Example: `cells_20230530.csv.gz`
- **Processed File Naming**: `<YYYYMMDD>.LOADED`
  - Example: `cells_20230530.csv.20230531.LOADED`
- **HDFS Landing Zone**: `/ez/landingzone/REFDATA`

### Scripts & Logs Locations
- **Node**: `un2.bigdata.abc.gr (999.999.999.999)`
- **User**: `intra`
- **Scripts Path**: `/shared/abc/refdata/bin`
  - `210_refData_Load.sh`
  - `220_refData_Daily_Snapshot.sh`
- **Logs Path**: `/shared/abc/refdata/log`
  - `210_refData_Load.<YYYYMM>.log`
  - `220_refData_Daily_Snapshot.<YYYYMM>.log`

### Crontab Scheduling
- **Node**: `un2.bigdata.abc.gr`
- **User**: `intra`
- **Runs**: Daily at `00:05 UTC`
```bash
5 0 * * * /shared/abc/refdata/bin/210_refData_Load.sh CELLS $(date '+\%Y\%m\%d' -d "yesterday")
```
For each reference type, a new **crontab entry** is required:
- `<reference Type>`: `cells, crm, devices, services`
- `<reference Date>`: Default is `yesterday`

### Hive Tables
- **Database**: `refdata`
- **Tables**:
  - `rd_cells_load`
  - `rd_services_load`
  - `rd_crm_load`
  - `rd_devices_load`

---

## 3. Data Processing

### High-Level Overview

![High_Level_Overview](https://metis.ghi.com/obss/bigdata/abc/alarm-archiving/refdata/-/raw/main/docs/ReferenceData.High_Level_Overview.png)

#### Steps:
1. **Data Preparation**:  
   - `abc` generates **Reference Data flat files**.
   - Files are stored on `UN2` via **SFTP PUT** (user `vantagerd`).
2. **Data Loading** (`210_refData_Load.sh`):
   - Reads, parses, and loads data into **Hive LOAD tables** (`rd_*_load`).
   - Data is stored in partitions **based on load date** (`par_dt=YYYYMMDD`).
3. **Snapshot Extraction** (`220_refData_Daily_Snapshot.sh`):
   - Extracts **latest** data from **LOAD tables**.
   - Stores them into **Snapshot tables** for **fact data enrichment** (e.g., Traffica).

---

## 4. Manually Run

The script `210_refData_Load.sh` can be **manually** executed with:
```bash
/shared/abc/refdata/bin/210_refData_Load.sh <refType> <refDate>
```
Where:
- `<refType>`: `CELLS`, `CRM`, `DEVICES`, `SERVICES`
- `<refDate>`: Date in `YYYYMMDD` format (extracted from filename)

### Example:
For the following files:
```
cells_20220207.csv.gz
cells_20220208.csv.gz
services_20220207.csv.gz
devices_20220208.csv.gz
crm_20220209.csv.gz
```
Run:
```bash
/shared/abc/refdata/bin/210_refData_Load.sh CELLS 20220207
/shared/abc/refdata/bin/210_refData_Load.sh CELLS 20220208
/shared/abc/refdata/bin/210_refData_Load.sh SERVICES 20220207
/shared/abc/refdata/bin/210_refData_Load.sh DEVICES 20220208
/shared/abc/refdata/bin/210_refData_Load.sh CRM 20220209
```

After execution, the files will be renamed to:
```
cells_20220207.csv.20230531.LOADED
cells_20220208.csv.20230531.LOADED
services_20220207.csv.20230531.LOADED
devices_20220208.csv.20230531.LOADED
crm_20220209.csv.20230531.LOADED
```

---

## 5. Monitoring & Debugging

**Note:** The **Reference Data Flow does NOT support Monitoring Services**.

### Alerts:
If a failure occurs, an **email alert** will be sent:
```
Subject: ALERT: Reference Data Loading, Type:CELL, File:cells_20220207.csv
Body:
    Reference Type  : CELL
    Reference File  : cells_20220207.csv
    Reference Script: 210_refData_Load.sh
    ------------------------------------------
    ERROR:$(date '+%F %T'), ALTER TABLE or LOAD DATA command failed.
```

### Log Analysis:
Check logs for errors:
```bash
egrep -i 'error|fail|exception|problem' /shared/abc/refdata/log/210_refData_Load.YYYYMM.log
egrep -i 'error|fail|exception|problem' /shared/abc/refdata/log/220_refData_Daily_Snapshot.YYYYMM.log
```
If a failure occurs, **re-run the script manually** as described in **Section 4**.

---

## 6. Troubleshooting

### Common Errors & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| **Reference data file is empty** | File has no data or incorrect format | Inform `abc` and request a **valid file** |
| **Hive/Impala availability issues** | Hive or Impala service down | Restart Hive/Impala |
| **Kerberos authentication issues** | Expired ticket | The flow performs `kinit` automatically |

---


## 7. Miscellaneous Notes

- The **Reference Data Flow** runs **daily at 00:05 UTC**.
- The **latest reference data** is **stored in Snapshot Tables** for fact data enrichment.
- **Monitoring logs** should be checked **daily** for failures.

## 8. Data Validation & Checks

### Check for New Partitions:
```bash
su - intra
/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k -q "refresh refdata.rd_cells_load; show partitions refdata.rd_cells_load;"
```
Example Output:
```
+----------+-----------+--------+---------+
| par_dt   | #Rows     | #Files | Size    |
+----------+-----------+--------+---------+
| 20220227 | 98090     | 1      | 41.88MB |
| 20220228 | 98021     | 1      | 41.84MB |
| 20220301 | 97353     | 1      | 41.76MB |
| Total    | 142404322 | 1500   | 59.63GB |
+----------+-----------+--------+---------+
```

### Check Data Count:
```bash
su - intra
/usr/bin/impala-shell -i un-vip.bigdata.abc.gr --ssl -k -q "select par_dt, count(*) as cnt from refdata.rd_cells_load group by par_dt order by 1;"
```
Example Output:
```
par_dt   | cnt    
---------+--------
20221130 | 2784494
```

---

