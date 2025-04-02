### Cube Indicators Pipeline

* Coordinator `1011_Fixed_brond_customers`  populates table `brond.fixed_brond_customers_daily`
* Coordinator `Coord_post_BROND_FIXED_CUSTOMERS` populates tables `brond.fixed_brond_customers_daily_unq` & `brond.fixed_customers_brond_latest`
* Coordinator `Coord_Cube_Spark_Indicators` for `par_date=date -2 days` populates table `brond.cube_indicators`  and its dependencies are:
  * `brond.fixed_radio_matches_unq_inp` populated by script `un2:/shared/abc/brond/bin/101_fixed_radius.sh`
  * `brond.fixed_brond_customers_daily_unq`
  * `radius.radacct_hist` populated by script `un2:/shared/abc/radius/DataParser/scripts/radius.pl`
  * `brond.brond_retrains_hist` populated by script `un2:/shared/abc/brond/DataParser/scripts/brond_retrains.pl`
  * `brond.dsl_stats_week_xdsl_hist` populated by Coordinator `coord_brond_load_dsl_daily_stats`
