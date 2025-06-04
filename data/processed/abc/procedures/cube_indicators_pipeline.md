---
title: "Cube Indicators Pipeline"
description: "Overview of the Brond Cube Indicators data pipeline, including Oozie coordinators, dependency tables, and the scripts responsible for generating input data."
tags:
  - brond
  - cube indicators
  - oozie
  - hadoop
  - coordinator
  - radius
  - retrains
  - fixed customers
  - data pipeline
  - xdsl
---
# Cube Indicators Pipeline
This document summarizes the data flow and dependencies of the `brond.cube_indicators` pipeline. It includes the Oozie coordinators involved, input tables, and the scripts or jobs that populate each dependency. The main output is the `brond.cube_indicators` table, populated for `par_date = today - 2 days`.
* Coordinator `1011_Fixed_brond_customers`  populates table `brond.fixed_brond_customers_daily`
* Coordinator `Coord_post_BROND_FIXED_CUSTOMERS` populates tables `brond.fixed_brond_customers_daily_unq` & `brond.fixed_customers_brond_latest`
* Coordinator `Coord_Cube_Spark_Indicators` for `par_date=date -2 days` populates table `brond.cube_indicators`  and its dependencies are:
  * `brond.fixed_radio_matches_unq_inp` populated by script `un2:/shared/abc/brond/bin/101_fixed_radius.sh`
  * `brond.fixed_brond_customers_daily_unq`
  * `radius.radacct_hist` populated by script `un2:/shared/abc/radius/DataParser/scripts/radius.pl`
  * `brond.brond_retrains_hist` populated by script `un2:/shared/abc/brond/DataParser/scripts/brond_retrains.pl`
  * `brond.dsl_stats_week_xdsl_hist` populated by Coordinator `coord_brond_load_dsl_daily_stats`
---
tags:
  - cube_indicators
  - brond
  - coordinator
  - radius
  - retrains
  - fixed_customers
  - xdsl
  - spark
  - hadoop
  - data_dependencies
---