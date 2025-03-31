# Kubernetes Certificate Renewal Procedure

## Description
This procedure outlines the steps required to renew Kubernetes certificates for the control plane nodes (`kubemaster1`, `kubemaster2`, and `kubemaster3`). The certificates expire annually and must be renewed to maintain cluster functionality.

## Prerequisites
- Access to Kubernetes master nodes (`kubemaster1`, `kubemaster2`, and `kubemaster3`).
- Root privileges on all master nodes.
- Downtime is required for this procedure.
- The `incelligent` user exists only on `kubemaster1`, so actions related to this user are not needed on `kubemaster2` and `kubemaster3`.

## Affected Systems / Scope
- **Kubernetes Control Plane Nodes:**
  - `kubemaster1.bigdata.abc.gr`
  - `kubemaster2.bigdata.abc.gr`
  - `kubemaster3.bigdata.abc.gr`
- **Kubernetes Services:**
  - API Server
  - Controller Manager
  - Scheduler
  - CoreDNS

---

## Procedure Steps

### **1. Login to `kubemaster1` as Root**
```bash
ssh kubemaster1.bigdata.abc.gr
sudo su -
```

---

### **2. Check Certificate Expiration**
```bash
kubeadm certs check-expiration
```

---

### **3. Backup Kubernetes Configuration and Service Accounts**
1. **Backup Kubernetes Configuration**
   ```bash
   cp -ar /etc/kubernetes /tmp/
   ```

2. **Backup `incelligent` Service Account Credentials**
   ```bash
   cp -ar /home/users/incelligent/.kube/config /tmp/bckup_renew_certificates/
   ```

---

### **4. Renew Kubernetes Certificates**
```bash
kubeadm certs renew all
kubeadm certs check-expiration
```

---

### **5. Update Kubernetes Configuration**
1. **Backup Current `admin.conf` File**
   ```bash
   cp -p /root/.kube/config /root/.kube/config_old
   ```

2. **Replace with the Newly Created `admin.conf`**
   ```bash
   cp /etc/kubernetes/admin.conf /root/.kube/config
   ```

3. **Update `incelligent` User's Kubernetes Configuration**
   - Copy `client-certificate-data` and `client-key-data` from `/etc/kubernetes/admin.conf`
   - Edit `incelligent` user's configuration file:
     ```bash
     vi /home/users/incelligent/.kube/config
     ```
   - Replace the old values with the new certificate details.

---

### **6. Verify Certificate Renewal**
```bash
kubeadm certs check-expiration
```

---

### **7. Check Kubernetes Functionality**
```bash
kubectl get pods
```

---

### **8. Restart Critical Control Plane Components**
1. **List Running Kubernetes Containers**
   ```bash
   ctrctl ps
   ```

2. **Stop the Following Containers**
   - Identify and stop containers related to:
     - `kube-controller-manager`
     - `kube-scheduler`
     - `kube-apiserver`
   ```bash
   ctrctl stop <container_id_1> <container_id_2> <container_id_3>
   ```

> **Warning:** When these containers are stopped, there will be downtime.  
> **Note:** These are static pods, so they will be automatically restarted.

---

### **9. Delete CoreDNS Pods**
1. **List CoreDNS Pods**
   ```bash
   kubectl get pod -n kube-system -l k8s-app=kube-dns
   ```

2. **Delete CoreDNS Pods**
   ```bash
   kubectl delete pod <coredns_pod_1> <coredns_pod_2> -n kube-system
   ```

---

### **10. Repeat the Same Procedure on `kubemaster2` and `kubemaster3`**
- Follow all the steps above, except for updating the `incelligent` user's configuration, which only exists on `kubemaster1`.

---

## Actions Taken / Expected Output
- **Certificates renewed successfully:** New certificates applied to all Kubernetes master nodes.
- **Kubernetes control plane restarted:** API Server, Controller Manager, and Scheduler automatically restarted.
- **CoreDNS restarted:** Ensuring DNS resolution within the cluster.
- **Cluster functionality verified:** Kubernetes is operational after certificate renewal.

## Notes and Warnings
> **Downtime is required** while control plane components restart.  
> **Ensure backups are taken** before proceeding with certificate renewal.  
> **The `incelligent` user exists only on `kubemaster1`**, so no changes are needed for this user on `kubemaster2` or `kubemaster3`.

## Troubleshooting / Error Handling
- **If Kubernetes does not start after renewal:**
  ```bash
  journalctl -xe -u kubelet
  ```
- **If `kubectl` commands fail:**
  ```bash
  kubectl get nodes
  kubectl get pods -A
  ```
- **Verify Control Plane Components are Running:**
  ```bash
  kubectl get pods -n kube-system
  ```

## References
