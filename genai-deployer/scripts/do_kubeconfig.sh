#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <cluster-name>"
  exit 1
fi

CLUSTER="$1"
echo "Fetching kubeconfig for cluster: $CLUSTER"
doctl kubernetes cluster kubeconfig save "$CLUSTER"
kubectl cluster-info
