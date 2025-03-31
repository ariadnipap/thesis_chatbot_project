### Certificate Authority installation

Below procedure describe the installation of a certificate authority using SaltStack.

 1.  Move given certificate under `admin:/etc/salt/salt/tls/internal_certificate/root_certificate/`
 2.  Rename `.cer` file to `.crt`.

- If certificate has `.crt` suffix you should first verify that it base64 encoded by opening file and make sure it starts with `-----BEGIN CERTIFICATE----`
 
 ```bash
mv /etc/salt/salt/tls/internal_certificate/root_certificate/certificate.crt /etc/salt/salt/tls/internal_certificate/root_certificate/certificate.cer
```
3. Install certificate by using saltStack formula:

```bash

###Test what actions will take affect before actually run the installation formula
salt 'node_name' state.apply tls.internal_certificate.install_root_certificate_os test=True

### Install the certificate
salt 'node_name' state.apply tls.internal_certificate.install_root_certificate_os
```

4. Install jssecacerts by using saltStack formula:

```bash
salt 'node_name' state.apply tls.internal_certificate.install_root_certificate_jssecacerts
```

> Ndef: Keep in mind that above command will fail if there is no java installed at the specified node

**Congratulations!**
