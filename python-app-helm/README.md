# Python App Helm Chart

This Helm chart deploys the Python microservices application from the `k8s-manifest` directory.

## Install

```bash
helm install python-app ./python-app-helm -f python-app-helm/values-dev.yaml
```

## Upgrade

```bash
helm upgrade python-app ./python-app-helm -f python-app-helm/values-prod.yaml
```

## Render templates

```bash
helm template python-app ./python-app-helm
```

## Files

- `Chart.yaml` – chart metadata
- `values.yaml` – default values
- `values-dev.yaml` – development overrides
- `values-prod.yaml` – production overrides
- `templates/` – Kubernetes manifests turned into Helm templates
