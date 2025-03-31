# NBG BigStreamrt Loging

## Citrix Remote Access

At first please follow the instructions [here](./KnowledgeBase/NBG/BigStreamer/system/accessibility/NBG_Remote_Access_Procedure_eng.pdf) in order to set up your personal Citrix Remote Access

## Login to Servers

Once you logged in with your account at `capam.groupnbg.com` you must be able to see all the VMS as seen below:

![](vms.PNG)


Login to any desired VM with the credentials  from  [here](https://metis.intracomtel.com/obss/oss/sysadmin-group/support/-/blob/master/KnowledgeBase/NBG/nbg-syspasswd.kdbx?ref_type=heads)


There are two sites, one for Primary and one for Disaster

From Desktop, open MobaXterm to connect to the servers (`dr1edge01` and `dr1edge02` for Disaster Site) and  (`pr1edge01` and `pr1edge02` for Primary Site) using your personal credentials

Note that in order to login to internal nodes you must first connect to edge nodes
