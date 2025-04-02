# How to create a keytab in NYMA

Login into kerb1 node as root

```bash
ssh kerb1
sudo -i
```

Use command-line interface to the Kerberos administration system

```bash
kadmin.local
```

Check if there is a principal for the corresponding username

```bash
listprincs <username>@CNE.abc.GR
```

Create a principal if there is not one

```bash
addprinc <username>CNE.abc.GR
```

Create the keytab

```bash
ktadd -k /tmp/<username>.keytab -norandkey <username>@CNE.abc.GR
```

Copy the keytab file to un2 node

```bash
scp -p /tmp/<username>.keytab un2:/tmp
```

Login into un2, place keytab file under /home/users/skokkoris/ and change ownership into skokkoris

```bash
ssh un2
sudo -i
cp -p /tmp/<username>.keytab /home/users/skokkoris/
chown skokkoris. /home/users/skokkoris/<username>.keytab
```
