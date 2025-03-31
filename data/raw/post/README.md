# Knowledge Base

This folder contains information on how to access customers' systems and troubleshoot them with information for applications/flows and troubleshooting information from past incidents.

## Table of contents

[TOC]

## Folder structure

## Index

[This](./index.md) is an index of past incidents either reported by the customer in Adares or internally via Gitlab Issues.

**# Customer** (for example abc)  

**## Project** (for example BigStreamer)  

**### Subproject** (for example EKL, if exists append the issue under this line)  

**Issue Number:** GI1 (GitLab Issue Number 1) or IM123456 (Adares Ticketing System Issue Number).  
**Description:** Title of the Incident/GitLab Issue  
**Keywords:** Add the appropriate keywords for better search. For example, if you faced anproblem with yum packages you should add a "yum" keyword here.  
**Owner:** Comma separated usernames of the oncall engineers that resolved it.  
**Date:** Date completed (format YYYYMMDD).  
**Status:** Open/Resolved/Workaround.  
**Info:** link to the actions taken for the request/incident.  

## Keywords

[This file](./keywords.md) contains the list of valid values for the "Adr Flex1" in ITSM as described [here](/onCall/README.md#incident-management-guidance)

## Customer folders

There is a seperate folder for each customer.

| **Customer** |     **Project**     |                        **Access Site**                         | **Enable Access** |
| :----------: | :-----------------: | :------------------------------------------------------------: | :---------------: |
|     mno      |      Big Data       |       [Remdef](./mno/BigStreamer/system/accessibility/)        |    [Matrix]()     |
|    Serbia    |  ActionStreamer NG  | [Remdef](./jkl/actionStreamer/system/accessibility/) |    [Matrix]()     |
|   abc    |   ActionStreamer    |    [Remdef](./abc/ActionStreamer/system/accessibility/)    |    [Matrix]()     |
|   abc    |        ASAP         |         [Remdef](./abc/ASAP/system/accessibility/)         |    [Matrix]()     |
|     Nexi     | Genesys CX Insights |        [Remdef](./Nexi/GenesysCX/system/accessibility/)        |    [Matrix]()     |
|    Police    |   Smart Policing    |    [On Site](./Police/Smart_Policing/system/accessibility/)    |    [Matrix]()     |
|   abc    |     BigStreamer     |     [Remdef](./abc/BigStreamer/system/accessibility/)      |    [Matrix]()     |
|     def      |      BDC PROD       |            [Remdef](./def/BDC/system/accessibility)            |    [Matrix]()     |
|     def      |       BDC DEV       |            [Remdef](./def/BDC/system/accessibility)            |    [Matrix]()     |
|   stu   |       Smarts        |       [Remdef](./stu/SMARTS/system/accessibility/)        |    [Matrix]()     |
|   stu   |   ActionStreamer    |   [Remdef](./stu/ActionStreamer/system/accessibility/)    |    [Matrix]()     |
|   stu   |      Daidalos       |      [Remdef](./stu/Daidalos/system/accessibility/)       |    [Matrix]()     |
|     vwx     |      Big Data       |         [Remdef](./vwx/BigData/system/accessibility/)         |    [Matrix]()     |
|     Yettel   |      Yettel       |         [Remdef](./Yettel/system/accessibility/)                 |    [Matrix]()     |
| Telecon Serbia |      ActionStreamer       |         [Remdef](./jkl/actionStreamer/system/accessibility/)                 |    [Matrix]()     |

Each customer consists of the following folders:

- **README.md** - Contains information about `project`.
- **map.md** - A brief map of project with useful links.
- **\<Customer\>-syspasswd.kdbx** - This file contains the passwords from `customer` system.
- **incidentReports** - For every `critical` case we create an incident report that is sent to the customer. The template exists [here](https://ghi.sharepoint.com/:w:/t/BigDataOBSS/EftnJYnlJG5HhvaKLU357ocBjyDw1rU9eprUZf4q2UVOWg?e=Yy0AX1)
- **system** - This folder contains all the neccesary information about how to access, network ip addressing and servers/services.
- **issues** - This folder contains all the issues from past incidents.
- **supportDocuments** - Support documents folder that consists of `procedures` and `application`/`flows` information.
