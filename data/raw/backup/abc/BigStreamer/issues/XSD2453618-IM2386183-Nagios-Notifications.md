# Traffic from sender nagios@bigdata.abc.gr

##  Description

Καλησπέρα σας ,
Παρατηρείται καθημερινά mail traffic με senders

nagios@bigdata.abc.gr
 20241003063537.8E45B2031700@admin.bigdata.abc.gr

Τα notifications από το  nagios δεν λειτουργουν εδώ και αρκετό καιρό.

Απο τι προέρχεται αυτή η κίνηση ;

##  Actions Taken

Αρχικά επικοινωνήσαμε με τον πελάτη και καταλήξαμε στο ότι επιθυμούν να μη λαμβάνουν κανενός είδους notification πλέον.

Συνεπώς προχωρήσαμε ως εξής:

1.  Login as root on admin.bigdata.abc.gr
2.  
```
Check logs inside /var/log/nagios/nagios.log

Στη συνέχεια ελέγξαμε το βασικό configuration του nagios service:

cd /etc/nagios
vi nagios.cfg, όπου η παράμετρος enable_notifications=1
```
3.  Προτείναμε να γίνουν disable τα notifications -> **enable_notifications=0** και να προχωρήσουμε σε εκ νέου restart του nagios service. Μετά την αλλαγή:
```
systemctl restart nagios
systemctl status nagio
```
4.  Log in the Nagios GUI (https://admin.bigdata.abc.gr/nagios) with our groupnet credentials and check the **Notifications** Tab. Τα incoming notifications σταμάτησαν από τη στιγμή του restart και έπειτα.

Useful info: https://support.nagios.com/forum/viewtopic.php?t=40328, https://bobcares.com/blog/nagios-turn-off-all-notifications/

