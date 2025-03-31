# Cube Indicators Pipeline

## Description
This procedure outlines the execution and dependencies of the Cube Indicators Pipeline, which populates various tables related to brond customer data.

## Prerequisites
- Access to the relevant coordinators and scripts.
- Permissions to execute scripts on `un2`.
- Knowledge of table dependencies in the `brond` schema.

## Procedure Steps

### 1. Execution of Coordinator `1011_Fixed_brond_customers`
- This coordinator populates the table:
  ```
  brond.fixed_brond_customers_daily
  ```

### 2. Execution of Coordinator `Coord_post_BROND_FIXED_CUSTOMERS`
- This coordinator populates the following tables:
  ```
  brond.fixed_brond_customers_daily_unq
  brond.fixed_customers_brond_latest
  ```

### 3. Execution of Coordinator `Coord_Cube_Spark_Indicators`
- Runs for `par_date=date -2 days` and populates the table:
  ```
  brond.cube_indicators
  ```
- Dependencies for this coordinator:
  - **`brond.fixed_radio_matches_unq_inp`**  
    - Populated by the script:
      ```bash
      un2:/shared/abc/brond/bin/101_fixed_radius.sh
      ```
  - **`brond.fixed_brond_customers_daily_unq`**  
  - **`radius.radacct_hist`**  
    - Populated by the script:
      ```bash
      un2:/shared/abc/radius/DataParser/scripts/radius.pl
      ```
  - **`brond.brond_retrains_hist`**  
    - Populated by the script:
      ```bash
      un2:/shared/abc/brond/DataParser/scripts/brond_retrains.pl
      ```
  - **`brond.dsl_stats_week_xdsl_hist`**  
    - Populated by the coordinator:
      ```
      coord_brond_load_dsl_daily_stats
      ```

## Actions Taken / Expected Output
- Coordinators and scripts should execute successfully.
- The table `brond.cube_indicators` should be populated with the expected data.
- Dependencies should be correctly processed by their respective scripts.

## Notes and Warnings
> Ensure that all scripts and coordinators execute in the correct order to prevent data inconsistencies.

## Affected Systems / Scope
- `brond` schema and associated tables.
- `radius` schema for historical account data.
- Execution of scripts on `un2`.

## Troubleshooting / Error Handling
- If a coordinator fails, check its execution logs for errors.
- Verify script execution by checking logs on `un2`:
  ```bash
  tail -f /shared/abc/brond/bin/101_fixed_radius.log
  ```
- Check database logs for inconsistencies in table updates.

## References

