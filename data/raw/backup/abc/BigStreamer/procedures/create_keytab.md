# How to Create a Keytab in NYMA

## Description
This procedure outlines the steps to create a keytab file in NYMA by using the Kerberos administration system.

## Prerequisites
- SSH access to `kerb1` as `root`.
- SSH access to `un2` for keytab file transfer.
- Kerberos administration privileges.

## Procedure Steps

### 1. Login into `kerb1` as Root
- Establish an SSH connection:
  ```bash
  ssh kerb1
  sudo -i
  ```

### 2. Access the Kerberos Administration System
- Open the Kerberos command-line interface:
  ```bash
  kadmin.local
  ```

### 3. Check if a Principal Exists
- Run the following command to check for an existing principal:
  ```bash
  listprincs <username>@CNE.abc.GR
  ```

### 4. Create a Principal (If Not Existing)
- If the principal does not exist, create it:
  ```bash
  addprinc <username>@CNE.abc.GR
  ```

### 5. Generate the Keytab File
- Use the following command to generate the keytab:
  ```bash
  ktadd -k /tmp/<username>.keytab -norandkey <username>@CNE.abc.GR
  ```

### 6. Copy the Keytab File to `un2`
- Transfer the keytab file to `un2`:
  ```bash
  scp -p /tmp/<username>.keytab un2:/tmp
  ```

### 7. Move and Change Ownership of the Keytab File
- SSH into `un2`:
  ```bash
  ssh un2
  sudo -i
  ```
- Move the keytab file to the correct location:
  ```bash
  cp -p /tmp/<username>.keytab /home/users/skokkoris/
  ```
- Change ownership to `skokkoris`:
  ```bash
  chown skokkoris. /home/users/skokkoris/<username>.keytab
  ```

## Actions Taken / Expected Output
- The keytab file should be successfully created and securely stored.
- Running `listprincs` should confirm the existence of the principal.
- The keytab file should be transferred and owned by `skokkoris`.

## Notes and Warnings
> Ensure that the keytab file is transferred securely to prevent unauthorized access.

## Affected Systems / Scope
- Kerberos authentication system
- `kerb1` and `un2` nodes

## Troubleshooting / Error Handling
- If the principal does not exist, confirm the username format before creating one.
- If the `scp` transfer fails, verify SSH connectivity between `kerb1` and `un2`.
- Check Kerberos logs for issues:
  ```bash
  tail -f /var/log/krb5kdc.log
  ```

## References

