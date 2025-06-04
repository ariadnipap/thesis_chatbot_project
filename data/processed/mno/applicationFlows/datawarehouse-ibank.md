---
title: Datawarehouse IBank Extract and Export Processes
description: Comprehensive operational guide for extracting and exporting Internet Banking service data from `prod_trlog_ibank.service_audit` to detail tables and then to MSSQL via Sqoop. Includes scheduler setup (UC4), script paths, Spark and Sqoop jobs, troubleshooting, and historical retention notes.
author: produser / mno big data engineering
updated: 2025-05-01
tags:
  - datawarehouse
  - ibank
  - internet banking
  - spark
  - sqoop
  - uc4
  - dwh
  - produser
  - impala
  - extract
  - export
  - transfer
  - payment
  - card
  - loan payment
  - cancel payment
  - time deposit
  - mass debit
  - man date
  - my bank
  - service audit
  - yarn
  - staging
  - reconciliation
  - retention
  - monitoring
  - logs
---
# Datawarehouse ibank
## Extract
**Extraction of detail tables**
Our spark application will extract information from prod_trlog_ibank.service_audit table to different detail tables based on different service names with the help of lookup table service_name where needed. The columns of the detail tables are produced either from a non json column of the input table (eg. client_username) or from parsing the json fields request_text_data and response_text_data and extracting specific fields based on their name. When two fields have the same name then we will keep the greater value either for a number field or for a string based on lexicographic order.
These jobs are executed by the bank's scheduler. There is an agent installed on the BDA edge node which is called UC4. The UC4 agent executes the below script for every job:
**UC4 Agent Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh` on `dr1edge01.mno.gr` **OR** `pr1edge01.mno.gr` (according to which site is the active for the UC4 agent)
**User**: `PRODUSER`
**Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
The above script executes the below scripts for every job and the below scripts and each of these scripts executes this generic spark-submit script:
**Generic Spark Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submitter.sh`
The jobs which perform the extraction of the details from service_audit are:
### Transfer Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_transfer_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_transfer]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_transfer.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT TRANSFER
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t transfer
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t transfer -p 20191109
    ```
### Payment Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_payment_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_payment]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_payment.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT PAYMENT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t payment
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t payment -p 20191109
    ```
### Loan Payment Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_loanPayment_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_loan_payment]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_loan_payment.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT LOAN_PAYMENT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t loanPayment
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t loanPayment -p 20191109
    ```
### Cancel Payment Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_cancelPayment_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_cancel_payment]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_cancel_payment.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT CANCEL_PAYMENT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t cancelPayment
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t cancelPayment -p 20191109
    ```
### Card Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_card_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_card]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_card.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT CARD
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t card
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t card -p 20191109
    ```
### Stock Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_stock_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_stock]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_stock.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT STOCK
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t stock
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t stock -p 20191109
    ```
### Time Deposit Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_timeDeposit_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_time_deposit]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_time_deposit.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT TIME_DEPOSIT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t timeDeposit
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t timeDeposit -p 20191109
    ```
### Mass Debit Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_massDebit_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_mass_debit]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_mass_debit.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT MASS_DEBIT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t massDebit
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t massDebit -p 20191109
    ```
### Man Date Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_manDate_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_man_date]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_man_date.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT MAN_DATE
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t manDate
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t manDate -p 20191109
    ```
### My Bank Extract
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] --> B[Spark: PROD_IBank_DWH_myBank_YYYYMMDD-YYYYMMDD]
  B --> D[Impala: prod_trlog_ibank_analytical.dwh_details_my_bank]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/submit_my_bank.sh`
**User**: `PRODUSER`
**Spark Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_extract.log`
**Alert**:
- DWH_IBank EXTRACT MY_BANK
**Troubleshooting Steps**:
- Use the UC4 agent script logs and spark logs to identify the cause of the failure 
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t myBank
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/extract_details/sched_extract_details.sh -t myBank -p 20191109
    ```
---
## Export
**Export of details tables and part of service_audit columns to mno datawarehouse**
The data are copied temporary to an internal staging table with an impala query and then we use sqoop-export to export the data to Datawarehouse.
These jobs are executed by the bank's scheduler. There is an agent installed on the BDA edge node which is called UC4. The UC4 agent executes the below script for every job:
**UC4 Agent Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh` on `dr1edge01.mno.gr` **OR** `pr1edge01.mno.gr` (according to which site is the active for the UC4 agent)
**User**: `PRODUSER`
**Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
The above script executes the below scripts for every job and the below scripts and each of these scripts executes this generic sqoop script:
**Generic Sqoop Job Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_to_dwh.sh`
The jobs which perform the export of the details to the MSSQL Server are:
### Transfer Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_transfer] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_transfer_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_TransferDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.TransferDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_transfer.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT TRANSFER
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t transfer
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t transfer -p 20191109
    ```
### Payment Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_payment] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_payment_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_PaymentDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.PaymentDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_payment.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT TRANSFER
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t payment
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t payment -p 20191109
    ```
### Loan Payment Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_loan_payment] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_loan_payment_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_LoanPaymentDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.LoanPaymentDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_loan_payment.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT LOAN_PAYMENT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t loanPayment
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t loanPayment -p 20191109
    ```
### Cancel Payment Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_cancel_payment] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_cancel_payment_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_CancelPaymentDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.CancelPaymentDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_cancel_payment.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT CANCEL_PAYMENT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t cancelPayment
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t cancelPayment -p 20191109
    ```
### Card Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_card] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_card_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_CardDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.CardDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_card.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT CARD
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t card
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t card -p 20191109
    ```
### Stock Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_stock] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_stock_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_StockDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.StockDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_stock.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT STOCK
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t stock
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t stock -p 20191109
    ```
### Time Deposit Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_time_deposit] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_time_deposit_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_TimeDepositDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.TimeDepositDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_time_deposit.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT TIME_DEPOSIT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t timeDeposit
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t timeDeposit -p 20191109
    ```
### Mass Debit Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_mass_debit] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_mass_debit_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_MassDebitDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.MassDebitDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_mass_debit.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT MASS_DEBIT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t massDebit
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t massDebit -p 20191109
    ```
### Man Date Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_man_date] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_man_date_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_ManDateDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.TransferDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_man_date.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT MAN_DATE
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t manDate
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t manDate -p 20191109
    ```
### My Bank Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank_analytical.dwh_details_my_bank] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_my_bank_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_MyBankDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.MyBankDetails]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_my_bank.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT MY_BANK
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t myBank
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t myBank -p 20191109
    ```
### Service Audit Export
``` mermaid
  graph TD
  A[Impala: prod_trlog_ibank.service_audit] -->|Impala Insert| B[Impala: prod_trlog_ibank_analytical.dwh_details_service_audit_stg]
  B --> C[Sqoop: PROD_IBank_DWH_EXPORT_ServiceAuditDetails_YYYYMMDD-YYYYMMDD]
  C -->|Sqoop Export| D[MSSQL Server: InternetBankingDW.ServiceAudit]
  ```
**Submit Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/export_service_audit.sh`
**User**: `PRODUSER`
**Sqoop Logs**: Use Firefox on `dr1edge01.mno.gr`/`pr1edge01.mno.gr` to access the logs via YARN Resource Manager UI
**UC4 Agent Script Logs**: `/var/log/datawarehouse-ibank/PRODUSER/sched_export_to_dwh.log`
**Alert**:
- DWH_IBank EXPORT SERVICE_AUDIT
**Troubleshooting Steps**:
- Use the UC4 agent script logs and sqoop logs to identify the cause of the failure 
- The export job will not be executed if the previous day is not a business day
- The script cleans up after failure, so if the problem was temporary **communicate with mno UC4 administrators to rerun the job if you fixed the problem. If they ask us to rerun the job, then:**
  - For the previous day:
    ``` bash
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t serviceAudit
    ```
  - For a specified date:
    ``` bash
    # eg. 09-11-2019 (Ndef that the argument is one day after the desired date)
    /opt/ingestion/PRODUSER/datawarehouse-ibank/export_to_dwh/sched_export_to_dwh.sh -t serviceAudit -p 20191109
    ```
## Retention Mechanism (Suspended)
Ndef: **This mechanism is suspended. DO NOT Troubleshoot**. As of 22/09/2023 all tables listed bellow have been dropped by mno (**Mail Subject: Incident IM2220978 receipt confirmation. Related Interaction: SD2285018**).
Information shown here is for completeness.
**Execution**: Every day (at **3:30 pm in DR site** by **Cron**) 
**Description**: This script drops partitions from impala tables `prod_trlog_ibank_analytical.dwh_details*` older than 10 days.
**User**: `PRODUSER`
**Script Logs**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/retention_mechanism_daily.log`
**Script**: `/opt/ingestion/PRODUSER/datawarehouse-ibank/retention_mechanism_daily_STABLE.sh` on `dr1edge01.mno.gr`
**Alerts**:
- Retention DWH_retention {$table}
Where $table can be
- prod_trlog_ibank_analytical.dwh_details_cancel_payment
- prod_trlog_ibank_analytical.dwh_details_card
- prod_trlog_ibank_analytical.dwh_details_loan_payment
- prod_trlog_ibank_analytical.dwh_details_man_date
- prod_trlog_ibank_analytical.dwh_details_mass_debit
- prod_trlog_ibank_analytical.dwh_details_my_bank
- prod_trlog_ibank_analytical.dwh_details_payment
- prod_trlog_ibank_analytical.dwh_details_stock
- prod_trlog_ibank_analytical.dwh_details_time_deposit
- prod_trlog_ibank_analytical.dwh_details_cancel_transfer
**Troubleshooting Steps**:
- Use the script logs to identify the cause of the failure
- After the root cause for the failure is resolved, run manually the following command
  - To keep the only last 10 days:
    ``` bash
        /opt/ingestion/PRODUSER/datawarehouse-ibank/retention_mechanism_daily_STABLE.sh >> /opt/ingestion/PRODUSER/datawarehouse-ibank/retention_mechanism_daily.log 2>&1
    ```