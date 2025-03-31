# Certificate Authority Installation

## Description
This procedure describes the installation of a certificate authority using SaltStack.

## Prerequisites
- Ensure you have administrative access to the system.
- The required certificate file should be available before starting the procedure.
- Verify that SaltStack is installed and properly configured on the system.

## Procedure Steps

1. **Move the Certificate File**
   - Move the given certificate under the specified directory:
     ```bash
     mv /etc/salt/salt/tls/internal_certificate/root_certificate/certificate.crt /etc/salt/salt/tls/internal_certificate/root_certificate/certificate.cer
     ```

2. **Rename the Certificate File**
   - If the certificate has a `.cer` suffix, rename it to `.crt`.

3. **Verify the Certificate Format**
   - If the certificate has a `.crt` suffix, ensure that it is Base64 encoded:
     - Open the file and check that it starts with:
       ```
       -----BEGIN CERTIFICATE-----
       ```

4. **Install the Certificate Using SaltStack Formula**
   - First, test what actions will take effect before actually running the installation formula:
     ```bash
     salt 'node_name' state.apply tls.internal_certificate.install_root_certificate_os test=True
     ```
   - Then, install the certificate:
     ```bash
     salt 'node_name' state.apply tls.internal_certificate.install_root_certificate_os
     ```

5. **Install jssecacerts Using SaltStack Formula**
   - Run the following command to install jssecacerts:
     ```bash
     salt 'node_name' state.apply tls.internal_certificate.install_root_certificate_jssecacerts
     ```

## Actions Taken / Expected Output
- The certificate file should be moved and renamed correctly.
- The installation formula should complete successfully, and the certificate should be properly applied.
- The `jssecacerts` installation process should complete without errors.

## Notes and Warnings
> Keep in mind that the `salt 'node_name' state.apply tls.internal_certificate.install_root_certificate_jssecacerts` command will fail if there is no Java installed on the specified node.

## Affected Systems / Scope
- This procedure affects systems that rely on the installed certificate authority for authentication and secure communications.

## Troubleshooting / Error Handling
- If the certificate installation fails, verify that the certificate file exists in the correct directory.
- Ensure the certificate is properly formatted (Base64 encoded).
- If Java is not installed, install Java before running the `jssecacerts` installation command.
- Use the following command to check SaltStack logs for troubleshooting:
  ```bash
  tail -f /var/log/salt/minion
  ```

## References


