---
title: "Streamsets – Energy Efficiency Duplicate Resolution"
description: "Guide for accessing Streamsets for the Energy Efficiency pipeline and resolving duplicates in the 'energy_efficiency.cell' table using Impala."
tags:
  - streamsets
  - energy efficiency
  - duplicates
  - impala
  - sftp
  - hive
  - overwrite
  - bigd
  - par_dt
  - cell table
  - un2
---
# Streamsets - Energy Efficiency
This guide outlines how to access Streamsets for the Energy Efficiency pipeline, detect duplicate records in the `energy_efficiency.cell` table using Impala, and safely remove them by overwriting partitions.
## Streamsets Access
- **Login URL**: [https://999.999.999.999:18636/](https://999.999.999.999:18636/)
- **File Transfer (from `un2` using `sdc` user)**:
```bash
sftp bigd@999.999.999.999
cd /ossrc
```
## Check for Duplicates in Table
Run the following Impala queries to inspect duplicate records in the energy_efficiency.cell table:
```sql
-- Total rows by partition
SELECT count(*), par_dt 
FROM energy_efficiency.cell 
WHERE par_dt > '202111201' 
GROUP BY par_dt 
ORDER BY par_dt DESC;
-- Check for duplicates on a specific date
SELECT count(*) 
FROM (
  SELECT DISTINCT * 
  FROM energy_efficiency.cell 
  WHERE par_dt = '20211210'
) a;
```
## Reolve Duplicates
### 1. Create a Backup Table
```sql
CREATE TABLE energy_efficiency.cell_bak LIKE energy_efficiency.cell;
INSERT INTO TABLE energy_efficiency.cell_bak PARTITION (par_dt)
SELECT * FROM energy_efficiency.cell;
```
### 2. Overwrite the Original Table
Update the table using only distinct records for the specified partition range:
```sql
INSERT OVERWRITE TABLE energy_efficiency.cell PARTITION (par_dt)
SELECT DISTINCT * 
FROM energy_efficiency.cell 
WHERE par_dt BETWEEN '20211210' AND '20211215';
```
### 3. Drop the Backup Table (if cleanup confirmed)
```sql
DROP TABLE energy_efficiency.cell_bak;
```
---
tags:
  - streamsets
  - impala
  - hive
  - data deduplication
  - energy efficiency
  - par_dt
  - partition overwrite
  - data cleanup
  - sftp access
---