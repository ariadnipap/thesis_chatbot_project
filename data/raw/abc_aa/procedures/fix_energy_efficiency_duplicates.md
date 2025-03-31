# Streamsets - Energy Efficiency

## Access

Streamsets Login Page: https://999.999.999.999:18636/

Files:

From un2 with sdc user:

```bash
sftp bigd@999.999.999.999
cd /ossrc
```

## Check for Duplicates

Execute the following from Impala

```bash
select count(*), par_dt from energy_efficiency.cell where par_dt>'202111201' group by par_dt order by par_dt desc;
```

```bash
select count(*) from (select distinct * from energy_efficiency.cell where par_dt='20211210') a;
```

## Solve Duplicates

Execute the following from Impala

Backup table:
```bash
CREATE TABLE  energy_efficiency.cell LIKE energy_efficiency.cell;
INSERT INTO TABLE energy_efficiency.cell_bak PARTITION (par_dt) SELECT * FROM energy_efficiency.cell;
```

Modify table:
```bash
INSERT OVERWRITE TABLE energy_efficiency.cell partition (par_dt)
	SELECT DISTINCT * FROM energy_efficiency.cell
	WHERE par_dt between '20211210' and '20211215';
```

Drop Backup table:
```bash
DROP TABLE energy_efficiency.cell;
```
