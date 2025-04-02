# Scope

Once a year the kubernetes certificates are expiring. In order to prevent that, we have a procedure below in which we are describing the steps that will help you to renew them.

## Setup
**Masters**: `kubemaster1`, `kubemaster2`, `kubemaster3`

**Important ndef:** This procedure requires downtime.

## Procedure

Login to kubemaster1.bigdata.abc.gr with your personal account and become root:

- Check the certificates expiration date:
 
    ```bash
    sudo su -
    
    kubeadm certs check-expiration
    ```

- Keep a backup of kubernetes configuration to tmp 
    ```bash
    cp -ar /etc/kubernetes /tmp/
    ```

- Keep a backup of incelligent service account

```bash
cp -ar /home/users/incelligent/.kube/config /tmp/bckup_renew_certificates/
```

- Renew the certificates
    ```bash
    kubeadm  certs renew all
    kubeadm certs check-expiration
    ```

- Run the following
    ```bash
    cp -p /root/.kube/config /root/.kube/config_old
    cp /etc/kubernetes/admin.conf  /root/.kube/config
    ```

- From the newly create`/etc/admin/conf` make sure to copy the `client-certificate-data` and `client-key-data` data content. After that, ` vi /home/users/incellignet/.kube/config` and replace the values you copied earlier in order to add the new certificates.

- Check again the certificates expiration date
    ```bash
    kubeadm certs check-expiration
   ```

- Check the kubectl functionality
    ```bash
    kubectl get pods
    ```

- When the certificates of controller, apiserver and scheduler are renewed you must also stop containers of those three:

```bash
ctrctl ps
CONTAINER ID        IMAGE                  COMMAND                  CREATED             STATUS              PORTS               NAMES
1350c48cbfb5        b3c57ca578fb           "kube-controller-man…"   11 minutes ago      Up 11 minutes                           k8s_kube-controller-manager_kube-controller-manager-cti-cx1_kube-system_9eb854fb973ddd6df55fb792a2fbf743_9
1bd22e95ef01        5a84bb672db8           "kube-scheduler --au…"   11 minutes ago      Up 11 minutes                           k8s_kube-scheduler_kube-scheduler-cti-cx1_kube-system_649aa160f1bd0840b2bb0f70b6493f99_9
cf43799ae77d0       b6e18ffb844e6          "kube-apiserver --au…"   11 minutes ago      Up 11 minutes                 
```

Stop containers IDs:

```bash
ctrctl stop 1350c48cbfb5 1bd22e95ef01 cf3cb7655b99d
```

> Ndef_1: Keep in mind that when the containers will be stopped, there will be downtime

> Ndef_2: Keep in mind that those pods are static so you don't need to kill them. They will be automatically restarted

- Also delete core-dns pod:

```bash
kubectl get pod -n kube-system -l k8s-app=kube-dns
NAME                      READY   STATUS    RESTARTS      AGE
coredns-64897985d-7dzkl   1/1     Running   3 (84d ago)   644d
coredns-64897985d-rw5kc   1/1     Running   0             83d
```

```bash
kubectl delete pod coredns-64897985d-7dzkl  coredns-64897985d-rw5kc  -n kube-system
```

- Repeat the same procedure for `kubemaster2` and `kubemaster3`


> Ndef: incelligent user exists only at kubemaster1, so you dont have to to do actions for this users at kubemaster2 and kubemaster3