# Below procedure describes how to add a new repostiory on Nexus. 

1. Login with your personal account to an edge node and open firefox
```bash
ssh -X xedge0x
firefox
```
2. When firefox vwxow pops up login to `https://999.999.999.999:8081/` with Nexus creds.

[Click me for the credentials](https://metis.ghi.com/obss/oss/sysadmin-group/mno/cloudera-cluster/-/blob/master/Documentation/passwords.kdbx)

3. Click on the gear icon and then **repositories** button and **Create repository** and select **yum (proxy)**.

Add below values:
- **Name**: name_of_repo
- **Remdef storage**: remdef_storage_url 
- **Maximum Component age**: 20
- **Minimum Component age**: 20
- **Clean up policies**: daily_proxy_clean

Leave the rest of the settings as default

4. Click on **Create repository**

5. Login with your personal account at node and add the following repos:

```bash
vi /etc/yum.repos.d/name_of_repo.repo

[name_of_repos]
name = name_of_repo
baseurl = http://999.999.999.999:8081/repository/name_of_repo.repo
enabled = 1
gpgcheck = 0
```

6. Check and add new repo
```bash
ssh to_node
yum clean all
yum check-update > /tmp/test-repo.txt
yum repolist
```
