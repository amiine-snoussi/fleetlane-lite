#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-http://127.0.0.1:8000}"

v=$(curl -s -X POST "$BASE/api/vehicles" -H "Content-Type: application/json" \
  -d '{"plate":"ABC123","mileage":10,"location":"MTL"}')
echo "$v" | jq
vid=$(echo "$v" | jq -r .id)

c=$(curl -s -X POST "$BASE/api/customers" -H "Content-Type: application/json" \
  -d '{"name":"Test Customer","contact":"test@example.com"}')
echo "$c" | jq
cid=$(echo "$c" | jq -r .id)

r1=$(curl -s -X POST "$BASE/api/reservations" -H "Content-Type: application/json" \
  -d "{\"customer_id\":$cid,\"vehicle_id\":$vid,\"start_at\":\"2026-03-04T10:00:00\",\"end_at\":\"2026-03-04T12:00:00\"}")
echo "$r1" | jq
rid=$(echo "$r1" | jq -r .id)

echo "Expecting overlap = 409..."
code=$(curl -s -o /tmp/overlap.json -w "%{http_code}" -X POST "$BASE/api/reservations" \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\":$cid,\"vehicle_id\":$vid,\"start_at\":\"2026-03-04T11:00:00\",\"end_at\":\"2026-03-04T13:00:00\"}")
test "$code" = "409"
cat /tmp/overlap.json | jq

curl -s -X POST "$BASE/api/reservations/$rid/sign" \
  -H "Content-Type: application/json" -d '{"signed_by":"Amine"}' | jq

curl -s -X POST "$BASE/api/reservations/$rid/checkout" \
  -H "Content-Type: application/json" -d '{"mileage_out":11}' | jq

curl -s -X POST "$BASE/api/reservations/$rid/checkin" \
  -H "Content-Type: application/json" -d '{"mileage_in":20,"notes":"OK"}' | jq
