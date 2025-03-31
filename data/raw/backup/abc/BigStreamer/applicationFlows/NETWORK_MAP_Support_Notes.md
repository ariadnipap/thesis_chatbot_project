# def_NETWORK_MAP Flow (OneTicket)

## 1. Overview

The def_NETWORK_MAP Flow handles the extraction, transformation, and loading (ETL) of network data from an Oracle database into a Big Data system. It ensures the synchronization of network-related information across multiple systems.

---

## 2. Installation & Configuration

### Data Source Tables
- **Source System**: Oracle Database 11g Enterprise Edition  
- **Server**: `999.999.999.999:1521`
- **User**: `def_network_map`
- **SID**: `defsblf_rw`
- **Oracle Tables**:
  - `def_NETWORK_MAP.ACTIVITY`
  - `def_NETWORK_MAP.AFFECTED_CUSTOMERS`
  - `def_NETWORK_MAP.AFFECTED_OCT_WTT`
  - `def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT`
  - `def_NETWORK_MAP.OPEN_MW`
  - `def_NETWORK_MAP.OPEN_NTT`
  - `def_NETWORK_MAP.OPEN_OCT`
  - `def_NETWORK_MAP.OPEN_WTT`
  - `def_NETWORK_MAP.EXPORT_CTL`

### Scripts & Configuration
- **User**: `def_network_maps`
- **Scripts Path**: `HDFS:/user/def_network_maps/`
- **Configuration Path**: `HDFS:/user/def_network_maps/`
  - `oneTicket_env.sh` - Environment configuration
  - `OraExpData.tables` - List of tables for export/import
  - `monitoring.config` - Monitoring connection details
  - `oraclecmd.config` - Oracle connection details
  - `oneticket.keystore` - Oracle password file
- **Temp Directory**: `HDFS:/ez/landingzone/tmp/oneTicket`

### Export Data Location
- **Node**: Dynamically defined by Oozie  
- **Directory**: Dynamically defined by Oozie

### Logs
- **User**: `def_network_maps`
- **Logs Path**: `/user/def_network_maps/log`
- **Log Files**:
  - `101.OneTicket_OraMetaData.<YYYYMM>.log`
  - `102.OneTicket_OraData_CTRL.<YYYYMM>.log`
  - `103.OneTicket_OraData_Export_Import.<TABLE_NAME>.<UNIX-TIME>.log`
  - `104.OneTicket_OraData_Import_Hive.<UNIX-TIME>.log`

### Oozie Scheduling
- **User**: `def_network_maps`
- **Coordinator**: `def_NETWORK_MAP_Coordinator`
- **Schedule**: Every 5 minutes (`0,5,10,15,...,55 * * * *`)
- **Workflow**: `def_NETWORK_MAP_Workflow`
- **Bash Script**: `HDFS:/user/def_network_maps/100.OneTicket_Main.sh`

### Hive Tables
- **Target Database**: `def_network_map`
- **Tables**:
  - `def_NETWORK_MAP.ACTIVITY`
  - `def_NETWORK_MAP.AFFECTED_CUSTOMERS`
  - `def_NETWORK_MAP.AFFECTED_OCT_WTT`
  - `def_NETWORK_MAP.DEFECTIVE_NETW_ELEMENT`
  - `def_NETWORK_MAP.OPEN_MW`
  - `def_NETWORK_MAP.OPEN_NTT`
  - `def_NETWORK_MAP.OPEN_OCT`
  - `def_NETWORK_MAP.OPEN_WTT`

### Database CLI Commands
- **Beeline**:
  ```bash
  /usr/bin/beeline -u "jdbc:hive2://un-vip.bigdata.abc.gr:10000/def_network_map;principal=hive/_HOST@CNE.abc.GR;ssl=true;sslTrustStore=/usr/java/latest/jre/lib/security/jssecacerts;trustStorePassword=changeit"
  ```
- **Impala**:
  ```bash
  /usr/bin/impala-shell -i un-vip.bigdata.abc.gr -d def_network_map --ssl -k
  ```
- **Oracle**:
  ```bash
  sqlplus -s def_network_map/<PASSWORD>@999.999.999.999:1521/defsblf_rw
  ```
- **MySQL**:
  ```bash
  mysql -u monitoring -p -h 999.999.999.999 monitoring
  ```

---

## 3. Data Processing

### Workflow Steps
1. **Export Procedure (Oracle)**:
   - Prepares data in Oracle tables.
   - Updates `EXPORT_CTL.EXPORT_START_DT` with a timestamp.

2. **Import Procedure (BigStreamer)**:
   - Detects new data in `EXPORT_CTL.EXPORT_START_DT`.
   - Extracts data using:
     ```bash
     ./oracle_cmd.sh "select * from <table>" > ./<table>.exp
     ```
   - Moves data to HDFS:
     ```bash
     hdfs dfs -moveFromLocal ./<table>.exp .
     ```
   - Loads data into Hive tables.

3. **Validation & Statistics Computation**:
   - Runs `compute incremental stats` in Impala:
     ```bash
     compute incremental stats def_network_map.<table>;
     ```

---

## 4. Monitoring & Debugging

### Logs
- **Monitoring Database**: `monitoring`
- **Monitoring Table**: `jobstatus`
- **Connection Command**:
  ```bash
  /usr/bin/mysql -u monitoring -p -h 999.999.999.999 monitoring
  ```
- **List Last Load Messages**:
  ```sql
  SELECT * FROM jobstatus
  WHERE application='ONETICKET' AND job='def_NETWORK_MAP'
  ORDER BY system_ts DESC;
  ```
- **Check Monitoring Status**:
  ```bash
  curl --location --request GET 'http://un-vip.bigdata.abc.gr:12800/monitoring/app/check'
  ```

---

## 5. Troubleshooting

### Common Errors & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Load Delay | `EXPORT_START_DT` > 2 hours before `IMPORT_START_DT` | Investigate Oracle export procedure |
| Impala/Hive Unavailable | Impala service is down | Restart Impala |
| Kerberos Authentication Error | Expired credentials | Run `kinit` |
| Empty Query Results | No new data in Oracle | Confirm `EXPORT_CTL` timestamp |

**Example Check for Load Delay:**
```sql
SELECT EXPORT_START_DT, IMPORT_START_DT,
  CASE WHEN 24*(EXPORT_START_DT-IMPORT_START_DT) > 2 THEN 'ERROR' ELSE 'OK' END Load_Status
FROM EXPORT_CTL WHERE EXPORT_SEQUENCE=0;
```

---

## 6. Data Validation & Checks

### Check Data Consistency in Hive/Impala
```sql
SELECT * FROM (
  SELECT DISTINCT 'activity' tbl, upd_ts FROM def_network_map.activity UNION ALL
  SELECT DISTINCT 'affected_customers', upd_ts FROM def_network_map.affected_customers UNION ALL
  SELECT DISTINCT 'open_ntt', upd_ts FROM def_network_map.open_ntt
) a ORDER BY tbl;
```
- `upd_ts` should match `IMPORT_START_DT` in Oracle `EXPORT_CTL`.

---

## 7. Miscellaneous Notes

- The process runs **every 5 minutes**, overwriting previous data.
- If no new data is found, the job exits without performing any operations.
- Data consistency is verified at multiple points using **Oracle, Impala, and Hive queries**.

---

