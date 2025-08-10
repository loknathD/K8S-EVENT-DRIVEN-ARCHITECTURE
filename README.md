Advanced KEDA and Karpenter Setup with Kafka on Kubernetes (EKS)

Overview
This repo demonstrates an industry-grade event-driven autoscaling pipeline using KEDA for pod-level scaling based on Kafka lag, and Karpenter for node-level provisioning on Amazon EKS. Features include scale-to-zero, cooldown periods, PDBs for HA, mixed spot/on-demand instances, node expiration, and a custom Python consumer app processing JSON order data.

Architecture
1.Kafka Cluster (Strimzi): Handles event streaming.
2.Producer: Floods JSON messages to simulate load.
3.Consumer App: Python app processes orders, calculates totals/tax, scales via KEDA on lag >75.
4.KEDA: Event-driven HPA extension.
5.Karpenter: Provisions nodes JIT with spot mix for cost savings.
6. Monitoring/HA: Probes, PDBs, tolerations ensure reliability.

Prerequisites
- AWS EKS cluster (v1.28+).
- Helm, kubectl.
- IAM roles for Karpenter (see AWS docs).
- Docker repo for consumer image.

Installation Steps
1. Setup EKS Cluster: Use eksctl or console. Enable IAM OIDC.
2. Install Strimzi Kafka Operator: `helm install strimzi oci://quay.io/strimzi-helm/strimzi-kafka-operator --namespace scaling-demo --create-namespace`.
3. Install KEDA: `helm install keda kedacore/keda --namespace keda --create-namespace`.
4. Install Karpenter: Follow https://karpenter.sh/docs/getting-started/, incl. IAM and Helm.
5. Build/Push Consumer Image: Use Dockerfile.
6. Apply YAMLs: In order - namespace, kafka-cluster, topic, consumer-deployment, keda-scaledobject, producer-deployment, pdb, karpenter-nodepool, karpenter-ec2nodeclass, rbac, postgresql (optional), networkpolicy (optional).
7. Test Scaling:
   - Send sample data: `kcat -b kafka-cluster-kafka-bootstrap.scaling-demo.svc.cluster.local:9092 -t test-topic -P -l < test-data.json`.
   - Monitor: `kubectl get pods -n scaling-demo -w`, `kubectl get nodes -w`.
8. Cleanup: `kubectl delete -f .` and uninstall charts.

ENJOY :)

## Troubleshooting
- Lag not triggering? Check Kafka bootstrap servers.
- Nodes not provisioning? Verify Karpenter IAM roles and tags.

Fork and contribute!
