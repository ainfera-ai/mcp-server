#!/usr/bin/env bash
# MCP keyed inference smoke — signup → tools/call inference with Bearer header.
# Requires smoke-mcp.sh session flow + deployed bearer-from-request fix.
set -euo pipefail

API="${AINFERA_API_BASE:-https://api.ainfera.ai}"
URL="${MCP_URL:-https://mcp.ainfera.ai/mcp}"
HDR=(-H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream')

echo "── 1 · Signup (public) ──"
HANDLE="mcp-keyed-$(date +%s)"
SIGNUP=$(curl -fsS -X POST "$API/v1/agents/signup" \
  -H 'Content-Type: application/json' \
  -d "{\"agent_handle\":\"$HANDLE\",\"owner_source\":\"anonymous\"}")
KEY=$(echo "$SIGNUP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["api_key"])')
AID=$(echo "$SIGNUP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["agent_id"])')
echo "  agent_id=$AID"

echo "── 2 · MCP initialize (Bearer) ──"
curl -sS -D /tmp/mcp_k_headers.txt -o /tmp/mcp_k_init.txt -X POST "$URL" "${HDR[@]}" \
  -H "Authorization: Bearer $KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke-keyed","version":"1.0.0"}}}'

SID=$(tr -d '\r' < /tmp/mcp_k_headers.txt | awk '/^[Mm]cp-[Ss]ession-[Ii]d:/ {print $2}')
if [[ -z "${SID:-}" ]]; then
  echo "FAIL: no mcp-session-id"
  exit 1
fi

curl -sS -o /dev/null -X POST "$URL" "${HDR[@]}" \
  -H "Authorization: Bearer $KEY" \
  -H "mcp-session-id: $SID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

echo "── 3 · tools/call inference ──"
PAYLOAD=$(AGENT_ID="$AID" python3 <<'PY'
import json
import os

print(
    json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "inference",
                "arguments": {
                    "agent_id": os.environ["AGENT_ID"],
                    "model": "claude-haiku-4-5",
                    "messages": [{"role": "user", "content": "Reply with one word: routed"}],
                    "max_tokens": 10,
                },
            },
        }
    )
)
PY
)
OUT=$(curl -sS -X POST "$URL" "${HDR[@]}" \
  -H "Authorization: Bearer $KEY" \
  -H "mcp-session-id: $SID" \
  -d "$PAYLOAD")

if echo "$OUT" | grep -q '"isError":true'; then
  echo "FAIL: inference tool returned error"
  echo "$OUT" | head -c 2000
  exit 1
fi

if ! echo "$OUT" | grep -qi 'routed\|content'; then
  echo "FAIL: unexpected inference response"
  echo "$OUT" | head -c 2000
  exit 1
fi

echo "OK: MCP inference tool succeeded (session ${SID:0:8}…)"

echo "── 4 · Audit verify ──"
curl -fsS "$API/v1/audit/$AID/verify" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('valid') is True, d
print('  audit valid:', d.get('event_count'), 'events')
"
