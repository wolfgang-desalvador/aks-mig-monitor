# AKS MIG Monitor
This repository contains the definition of a small experimental DaemonSet that allows to prevent scheduling on AKS nodes which are changing MIG profile through AKS

## How it works
This DaemonSet relies on a Service Account to taint the nodes in case the MIG configuration is not completed successfully. This becomes useful in case nodes are boot from scratch in autoscaling.

## How to use it

The DaemonSet can be configured on an existing AKS cluster with these prerequisites:

* A kubectl CLI configured and connected to the cluster with the required authorization
* An Azure Container Registry (ACR) attached to the AKS cluster
* A Docker enabled VM connected to the Azure Container Registry with AcrPush permission

To build and deploy the DaemonSet assumint that it will be deployed in `NAMESPACE` and using ACR `ACR_NAME`:


```bash
export NAMESPACE=<YOUR_NAMESPACE>
export ACR_NAME=<YOUR_ACR_NAME>
git clone https://github.com/wolfgang-desalvador/aks-mig-monitor.git
cd aks-mig-monitor
sed -i "s/<ACR_NAME>/$ACR_NAME/g" mig-monitor-daemonset.yaml
sed -i "s/<NAMESPACE>/$NAMESPACE/g" mig-monitor-roles.yaml
docker build . -t $ACR_NAME/aks-mig-monitor
docker push $ACR_NAME/aks-mig-monitor
kubectl apply -f mig-monitor-roles.yaml -n $NAMESPACE
kubectl apply -f mig-monitor-daemonset.yaml -n $NAMESPACE
```

