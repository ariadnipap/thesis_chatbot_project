# Streamsets - Energy Efficiency

## Description
This procedure outlines the steps to access Streamsets, check for duplicates in the `energy_efficiency.cell` table, and resolve them using Impala.

## Prerequisites
- Access to the Streamsets login page.
- SSH access to `un2` as the `sdc` user.
- Permissions to run queries in Impala on the `energy_efficiency.cell` table.

## Procedure Steps

### 1. Access Streamsets
- Open the login page:
  ```
  https://999.999.999.999:18636/
  ```

### 2. Access Files from `un2`
- Connect via SFTP as `sdc` user:
  ```bash
  sftp bigd@999.999.999.999
  cd /ossrc
  ```

### 3. Check for Duplicates in Impala
- Run the following query to check for duplicate records based on `par_dt`:
  ```bash
  select count(*), par_dt from energy_efficiency.cell where par_dt>'202111201' group by par_dt order by par_dt desc;
  ```
- Run the following query to count distinct records for a specific date:
  ```bash
  select count(*) from (select distinct * from energy_efficiency.cell where par_dt='20211210') a;
  ```

### 4. Solve Duplicates in Impala
#### **Backup the Table**
- Create a backup before modifying the data:
  ```bash
  CREATE TABLE energy_efficiency.cell_bak LIKE energy_efficiency.cell;
  INSERT INTO TABLE energy_efficiency.cell_bak PARTITION (par_dt) SELECT * FROM energy_efficiency.cell;
  ```

#### **Modify the Table**
- Remove duplicate records for a specific date range:
  ```bash
  INSERT OVERWRITE TABLE energy_efficiency.cell partition (par_dt)
    SELECT DISTINCT * FROM energy_efficiency.cell
    WHERE par_dt between '20211210' and '20211215';
  ```

#### **Drop the Backup Table**
- Once confirmed, remove the backup:
  ```bash
  DROP TABLE energy_efficiency.cell;
  ```

## Actions Taken / Expected Output
- The `energy_efficiency.cell` table is checked for duplicate records.
- Duplicate records are removed while preserving unique entries.
- A backup is created before modification to ensure data integrity.

## Notes and Warnings
> Ensure that a backup is created before modifying the table.  
> Verify the distinct records before executing the `INSERT OVERWRITE` command.

## Affected Systems / Scope
- **Streamsets**
- **Impala**
- **Energy Efficiency Data Pipeline**

## Troubleshooting / Error Handling
- If Impala queries fail, check the connection:
  ```bash
  impala-shell -i <impala-host>
  ```
- If data inconsistencies persist, restore from the backup table before dropping it.

## References
