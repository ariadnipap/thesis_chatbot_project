# Kubernetes User Environment Setup

## Description
This procedure outlines the steps to set up a Kubernetes user environment, including installing necessary tools, creating a service account, and configuring user authentication.

## Prerequisites
- Administrative or sudo privileges for installation.
- Internet access to download required tools.
- Kubernetes cluster access for service account creation.
- Required YAML configuration files for service account setup.

## Procedure Steps

### 1. Install `kubectl`
- Follow the installation instructions from the official Kubernetes documentation:  
  [Install `kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- Enable command completion:
  ```bash
  mkdir -p /etc/bash_completion.d
  kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl
  ```

### 2. Install Optional `kubectl` Plugin
- If needed, install the plugin for setting up kubeconfigs:  
  [kubectl-view-serviceaccount-kubeconfig-plugin](https://github.com/superbrothers/kubectl-view-serviceaccount-kubeconfig-plugin/releases)
- Place the binary under:
  ```bash
  /usr/local/bin/
  ```

### 3. Install `helm`
- Follow the [installation instructions](https://helm.sh/docs/intro/install/).
- Enable Helm command completion:
  ```bash
  helm completion bash | sudo tee /etc/bash_completion.d/helm
  ```

### 4. Create a Kubernetes Service Account
- Create a file named **`service_account.yml`** with the following content:
  ```yaml
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: <Account Name>
    namespace: <RAN.AI Namespace>
  ```
- Create a file named **`role_binding.yml`** with the following content:
  ```yaml
  kind: RoleBinding
  apiVersion: rbac.authorization.k8s.io/v1
  metadata:
    name: <Binding Name>
    namespace: <RAN.AI Namespace>
  subjects:
  - kind: ServiceAccount
    name: <Account Name>
    namespace: <RAN.AI Namespace>
  roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: edit
  ```
- Apply the configurations:
  ```bash
  kubectl apply -f service_account.yml
  kubectl apply -f role_binding.yml
  ```

### 5. Create a User Secret (For Kubernetes v1.24+)
- If using Kubernetes v1.24 or later, the secret is not automatically created. Create a file named **`user_secret.yml`**:
  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: <Account Secret Name>
    namespace: <RAN.AI Namespace>
    annotations:
      kubernetes.io/service-account.name: <Account Name>
  type: kubernetes.io/service-account-token
  ```
- Apply the secret:
  ```bash
  kubectl apply -f user_secret.yml
  ```

### 6. Retrieve User Configuration
- If the `kubectl-view-serviceaccount-kubeconfig` plugin is available:
  ```bash
  kubectl view-serviceaccount-kubeconfig -n <RAN.AI Namespace> <Account Name> > <User's Home>/.kube/config
  ```
- If the plugin is not available, construct the config manually.

### 7. Manually Construct Kubernetes Configuration
- A typical `config` file should look like this:
  ```yaml
  apiVersion: v1
  clusters:
  - cluster:
      certificate-authority-data: ...
      server: https://<Server>:<Port>
    name: <Cluster Name>
  contexts:
  - context:
      cluster: <Cluster Name>
      namespace: <RAN.AI Namespace>
      user: <Account Name>
    name: kubernetes-admin@kubernetes
  current-context: kubernetes-admin@kubernetes
  kind: Config
  preferences: {}
  users:
  - name: <Account Name>
    user:
      token: ...
  ```
- To retrieve the necessary values:
  ```bash
  # Find the Account's Secret Token name
  kubectl get secrets -n <RAN.AI Namespace>

  # Get certificate-authority-data
  kubectl get -n <RAN.AI Namespace> secret <Account Secret Token> -o jsonpath='{.data.ca\.crt}'

  # Get token (decoded)
  kubectl get -n <RAN.AI Namespace> secret <Account Secret Token> -o jsonpath='{.data.token}' | base64 --decode
  ```

## Actions Taken / Expected Output
- `kubectl` and `helm` should be installed and configured with command completion enabled.
- The service account and role binding should be created successfully.
- User authentication should be set up using a generated key.
- Kubernetes config file should be correctly populated and functional.

## Notes and Warnings
> For Kubernetes v1.24 and later, the service account secret is **not** automatically generated.  
> If using a manually constructed config, ensure the correct values are retrieved from the secret.

## Affected Systems / Scope
- Kubernetes Cluster
- Helm Package Manager
- User Authentication and Role-Based Access Control (RBAC)

## Troubleshooting / Error Handling
- If `kubectl` commands fail, verify that `kubectl` is installed correctly:
  ```bash
  kubectl version --client
  ```
- If unable to connect to the cluster, check the config file:
  ```bash
  cat ~/.kube/config
  ```
- If authentication fails, check that the correct token is retrieved:
  ```bash
  kubectl get secrets -n <RAN.AI Namespace>
  ```
- If installation issues persist, review logs:
  ```bash
  journalctl -u kubelet --no-pager | tail -n 50
  ```

## References
- [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [Install Helm](https://helm.sh/docs/intro/install/)

