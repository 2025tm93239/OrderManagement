#!/usr/bin/env bash
# Register Order API service, route /api/orders, and rate limiting (5 req/min).
set -euo pipefail

KONG_ADMIN="${KONG_ADMIN:-http://127.0.0.1:8002}"
UPSTREAM="${UPSTREAM:-http://host.docker.internal:8001/orders}"

echo "Kong Admin: $KONG_ADMIN"
echo "Upstream:   $UPSTREAM"

curl -sS -X POST "$KONG_ADMIN/services" \
  --data name=order-api-service \
  --data "url=$UPSTREAM" | jq .

SERVICE_ID=$(curl -sS "$KONG_ADMIN/services/order-api-service" | jq -r .id)

curl -sS -X POST "$KONG_ADMIN/services/$SERVICE_ID/routes" \
  --data name=orders-route \
  --data 'paths[]=/api/orders' \
  --data strip_path=true \
  --data 'methods[]=GET' \
  --data 'methods[]=POST' | jq .

curl -sS -X POST "$KONG_ADMIN/services/$SERVICE_ID/plugins" \
  --data name=rate-limiting \
  --data config.minute=5 \
  --data config.policy=local \
  --data config.limit_by=ip | jq .

echo "Kong setup complete."
