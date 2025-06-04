---
title: "Kubernetes User Environment Setup"
description: "Step-by-step guide to install kubectl and helm, create Kubernetes service accounts, and generate user-specific kubeconfig for RAN.AI environments."
tags:
  - kubernetes
  - kubectl
  - service account
  - kubeconfig
  - user setup
  - helm
  - role binding
  - authentication
  - secret
  - RAN.AI
---
# Kubernetes User Environment Setup
This guide explains how to set up a user environment for Kubernetes access in a RAN.AI cluster. It covers kubectl and helm installation, service account creation, role bindings, secrets, and kubeconfig generation—manually or using a plugin.
## Tools
The main tool that needs to be installed is **kubectl**, instructions for which can be found
[here](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/).
### Install bash completion for kubectl:
Additionally after
installation, completion can be enabled by executing:
```bash
mkdir -p /etc/bash_completion.d
kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl
```
If possible a nice to have plugin for setting up kubeconfigs can be found at
[kubectl-view-serviceaccount-kubeconfig-plugin](https://github.com/superbrothers/kubectl-view-serviceaccount-kubeconfig-plugin/releases). Simply place the binary under `/usr/local/bin/`.
Additionally in order to install **helm**, follow the [instructions](https://helm.sh/docs/intro/install/)
and set up completion by executing the following:
```bash
helm completion bash | sudo tee /etc/bash_completion.d/helm
```
## Service Account
Create the following YAML files, that contain the definition for the service account and its
role binding:
- **`service_account.yml`**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: <Account Name>
  namespace: <RAN.AI Namespace>
```
- **`role_binding.yml`**
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
### Apply service account and role binding
```bash
kubectl apply -f service_account.yml
kubectl apply -f role_binding.yml
```
### User Secret
For Kubernetes versions over 1.24 when creating a service account it's secret is not automatically created
and mounted, so in that case create the following secret:
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
### Generate user kubeconfig using plugin:
Execute the following to get the new users config. If the plugin is not available the config must be constructed manually:
```
kubectl view-serviceaccount-kubeconfig -n <RAN.AI Namespace> <Account Name> > <User's Home>/.kube/config
```
For reference the config looks like this:
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
In the above segment `certificate-authority-data` and `token` can be obtained by executing:
```bash
# Find the Account's Secret Token name
kubectl get secrets -n <RAN.AI Namespace>
kubectl get -n <RAN.AI Namespace> secret <Account Secret Token> -o jsonpath='{.data.ca\.crt}'
kubectl get -n <RAN.AI Namespace> secret <Account Secret Token> -o jsonpath='{.data.token}' | base64 --decode
```