How to enable acls in spark and yarn in two steps, in order to give access to spark logs for some specific groups
1. Yarn configuration

a. Go to yarn --> configuration then search for "acl"

The field we need to modify is "ACL For Viewing A Job"
And we've added extra groups in order to view map-reduce jobs.

example:  `hue WBDADMIN,WBDOPDEV,WBDOPPRO,WBDOPQA`

You must be very careful with the syntax, click the question mark 

b. Also we need to Enable Job ACL JobHistory Server Default Group

2. Spark configuration

Go to spark --> configuration then search for "Spark Client Advanced Configuration Snippet"

Then enable spark acl by adding the following line:

`spark.acls.enable=true`

& enable the acls for admin groups

`spark.admins.acls.groups=WBDADMIN`

Also add the following in order to give permissions to spark history server into a group

`spark.history.ui.admin.acls.groups=WBDADMIN`

Lastly, add the following which is the groups

`spark.ui.view.acls.groups=WBDOPDEV,WBDOPPRO,WBDOPQA`
