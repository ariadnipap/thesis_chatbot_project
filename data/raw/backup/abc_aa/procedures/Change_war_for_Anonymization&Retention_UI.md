# abc - Permanent Anonymization & Retention UI issue

<b>Description:</b>

```
Σχετικά με το πρόβλημα που υπάρχει στο UI του Permanent Anonymization & Retention (https://cne.def.gr:8643/customapps)
Να θυμίσω ότι η πρόσβαση στο συγκεκριμένο UI δεν είναι εφικτή μέσω VPN.
Ο λόγος είναι ότι προσπαθεί να φορτώσει μια βιβλιοθήκη από το internet (cdn.jsdelivr.net). 
Έγινε προσθήκη στο νέο war το οποίο πρέπει να μπει στην θέση του παλιού στους wildfly.
```

<b>Actions Taken:</b>

1. ssh with you personal account @unc2
2. sudo -i; less /etc/haproxy/haproxy.cfg and search for backend `tru-backend`.
3. Backup the old war file `ssh @unekl1; cp -rp /opt/trustcenter/wf_cdef_trc/standalone/deployments/wftrust-landing-web.war /opt/trustcenter/wf_cdef_trc/standalone/wftrust-landing-web.war.bkp`
4. chown trustuser:trustcenter `<new_war_file>`; chmod 644 `<new_war_file>`
5. mv `<new_war_file>` /opt/trustcenter/wf_cdef_trc/standalone/deployments/
6. Restart of wildfly is not `necessary`. Automaticcaly a new `wftrust-landing-web.war.deployed` will be created
7. su - trustuser; bash ; trust-status `to check that wildfly is running`
8. Make the same changes `@unekl2`
9. Clear your cache and try again `https://cne.def.gr:8643/customapps`

<b>Affected Systems:</b>

abc Bigstreamer


