# SSL Configuration Changes

[[_TOC_]]

All procedures pertain to PR and DR edge nodes:
- pr1edge01
- pr1edge02
- dr1edge01
- dr1edge02

## Preparation

Before continuing with the changes it is best to put the edge node you are
working on in standby mode, so as to not disrupt services:

    $ ssh Exxxx@XXXedgeXX
    $ sudo -i

And follow the procedures described in the **Switchover of Cluster Resources** chapter
of the **Security Vulnerabilities** MOP [here](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/MOP/21324_security_vulnerabilities_v3.docx).

## httpd

Backup the old httpd configs:

    # cp –ap /etc/httpd/conf.d/ssl.conf  "/etc/httpd/conf.d/ssl.conf.bak.$(date +%Y%m%d)"
    # cp –ap /etc/httpd/conf/httpd.conf  "/etc/httpd/conf/httpd.conf.bak.$(date +%Y%m%d)"
    # cp -ap /etc/httpd/conf.d/graphite-web.conf "/etc/httpd/conf.d/graphite-web.conf.bak.$(date +%Y%m%d)"

Add the following line in `/etc/httpd/conf/httpd.conf`:

    TraceEnable Off

Add the following line in `/etc/httpd/conf/httpd.conf`, `/etc/httpd/conf.d/ssl.conf`
and `/etc/httpd/conf.d/graphite-web.conf`:

    SSLProtocol +TLSv1.2

Edit `/etc/httpd/conf/httpd.conf`, `/etc/httpd/conf/ssl.conf` and
`/etc/httpd/conf/graphite-web.conf` and remove the following lines:

    SSLHonorCipherOrder Off
    SSLCipherSuite ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES256:ECDH+AES128:!aNULL:!SHA1:!AESCCM:!MD5:!3DES:!DES:!IDEA

Restart the **httpd** service:

    # systemctl restart httpd

## nginx

Backup the old **nginx.conf**:

    # cp -ap /etc/nginx/nginx.conf "/etc/nginx/nginx.conf.bak.$(date +%Y%m%d)"

Add the following line in `/etc/nginx/nginx.conf`:

    ssl_protocols TLSv1.2;

Disable and restart the **nginx** service:

    # systemctl disable --now nginx
    # systemctl start nginx

## haproxy

Backup the old **haproxy.cfg**:

    # cp -ap /etc/haproxy/haproxy.cfg "/etc/haproxy/haproxy.cfg.bak.$(date +%Y%m%d)"

Add options for 8889 and 25002 port and repeat for **hue_vip**:

    bind 999.999.999.999:25002 ssl crt no-sslv3 /opt/haproxy/security/x509/node.haproxy.pem

Restart the **haproxy** service:

    # systemctl restart haproxy

## sshd

Backup the old **sshd_config**:

    # cp -ap /etc/ssh/sshd_config "/etc/ssh/sshd_config.bak.$(date +%Y%m%d)"

Edit the sshd config `/etc/ssh/sshd_config` and add the following:

    Ciphers aes256-ctr,aes192-ctr,aes128-ctr # 5.2.11
    KexAlgorithms ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha256

Restart the **sshd** service:

    # systemctl restart sshd
