# Kubernetes Evaluation

`deploy/kubernetes.yaml` runs the local API runtime in Kubernetes. It demonstrates pod hardening,
secret injection, health probes, custom policy mounting, and a ClusterIP service. It does not use
Cognito, S3, DynamoDB, or durable audit storage.

Use the AWS deployment for the repository's complete shared-pilot architecture. Use this manifest
for cluster-local integration testing.

## Build and Publish the Image

```bash
docker build -t registry.example.com/platform/secure-context-cache:0.7.0 .
docker push registry.example.com/platform/secure-context-cache:0.7.0
```

Create a deployment copy with the registry image:

```bash
sed 's|image: secure-context-cache:0.7.0|image: registry.example.com/platform/secure-context-cache:0.7.0|' \
  deploy/kubernetes.yaml > /tmp/acg-kubernetes.yaml
```

Review `/tmp/acg-kubernetes.yaml` before applying it.

## Create the Local Credential Secret

```bash
ACG_K8S_API_KEY=$(openssl rand -hex 32)
kubectl create secret generic agent-context-gateway-credentials \
  --from-literal=api-key="$ACG_K8S_API_KEY"
```

Keep the shell variable only for the verification request, then unset it. In a long-lived cluster,
use the organization's secret manager and rotation process.

## Deploy and Verify

```bash
kubectl apply -f /tmp/acg-kubernetes.yaml
kubectl rollout status deployment/agent-context-gateway
kubectl port-forward service/agent-context-gateway 8080:80
```

In another terminal:

```bash
curl -sS http://127.0.0.1:8080/health
curl -sS http://127.0.0.1:8080/v1/capsules \
  -H 'content-type: application/json' \
  -H "x-agent-api-key: $ACG_K8S_API_KEY" \
  -d '{
    "task_type": "iac_security",
    "path": "terraform/prod/payments/lambda.tf",
    "prompt": "Review this change",
    "agent_id": "local-agent",
    "environment": "prod"
  }'
```

The default manifest uses the sample repository included in the image.

## Use a Real Context Directory

Mount an approved read-only context through a PVC, CSI driver, projected volume, or trusted init
container, then set:

```yaml
env:
  - name: ACG_ALLOWED_REPO_ROOT
    value: /contexts/repo
volumeMounts:
  - name: context
    mountPath: /contexts/repo
    readOnly: true
```

Add `repo: /contexts/repo` to API requests. Do not mount a whole developer workspace, secret store,
or broad shared volume.

The current scanner is synchronous and the local cache is pod memory. Keep one replica unless the
client tolerates per-pod cache telemetry and no shared server-side audit persistence. A production
Kubernetes architecture needs shared source/slice/audit stores and workload identity.

## Hardening Checklist

- Use an immutable image digest rather than `latest`.
- Run in a dedicated namespace with ResourceQuota and LimitRange.
- Add NetworkPolicy for explicit ingress and egress.
- Terminate TLS at a trusted ingress or service mesh.
- Use workload identity or an enterprise identity proxy instead of a shared API key.
- Mount context and policy read-only.
- Export logs and audit records to centralized immutable storage.
- Add PodDisruptionBudget only after shared state and multi-replica behavior are designed.
- Scan/sign the image and enforce admission policy.

## Remove

```bash
kubectl delete -f /tmp/acg-kubernetes.yaml
kubectl delete secret agent-context-gateway-credentials
unset ACG_K8S_API_KEY
```
