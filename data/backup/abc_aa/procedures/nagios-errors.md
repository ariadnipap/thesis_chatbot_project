abc

BigStreamer

Nagios(admin)

Issue Number: - 
Title: Nagios Alarms & Errors
Description: 

To fix the following errors appearing in Nagios:
"/etc/bashrc: fork: retry: Resource temporarily unavailable" ,
"ssh_exchange_identification: Connection closed by remdef host" , 
"Return code of 255 is out of bounds"  

Keywords: logs fork bounds Connection closed

Owner: kpar

Date: 20210512

Status: closed

Actions Taken:  ssh to node admin as root then :

For "fork" error : 
-------------------
as root or nagios user: 

vi /home/nagios/.bashrc

 add 

ulimit -u 8888

ulimit -n 2222


For Connection closed error ( "ssh_exchange_identification: Connection closed by remdef host"):
--------------------------------------------------------------------------------------------------

as root in file :  

vi /usr/local/nagios/etc/objects/commands.cfg 

change :

$USER1$/check_by_ssh  -H $HOSTADDRESS$ -t 30 -C "/usr/lib/nagios/plugins/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$"

to:

$USER1$/check_by_ssh -E 8 -o StrictHostKeyChecking=no -H $HOSTADDRESS$ -t 30 -C "/usr/lib/nagios/plugins/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$"
 

To stop "Return code of 255 is out of bounds" errors 
-------------------------------------------------------

as root:

In file /usr/local/nagios/etc/nagios.cfg , 
change value "max_concurrent_checks" from 0 to 50 , and then restart nagios :

#service nagios restart
 

