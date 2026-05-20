#!/usr/bin/env bash
# MCP end-to-end smoke — mcp.ainfera.ai (AIN-208 reference adapter proof)
set -euo pipefail

URL="${MCP_URL:-https://mcp.ainfera.ai/mcp}"
HDR=(-H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream')

init=$(curl -sS -D /tmp/mcp_headers.txt -o /tmp/mcp_init_body.txt -X POST "$URL" "${HDR[@]}" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke-mcp","version":"1.0.0"}}}')

session=$(tr -d '\r' < /tmp/mcp_headers.txt | awk '/^[Mm]cp-[Ss]ession-[Ii]d:/ {print $2}')
if [[ -z "${session:-}" ]]; then
  echo "FAIL: no mcp-session-id header"
  exit 1
fi

tools=$(curl -sS -X POST "$URL" "${HDR[@]}" -H "mcp-session-id: $session" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}')

count=$(echo "$tools" | python3 -c "
import re, json, sys
t = sys.stdin.read()
m = re.search(r'data: ({.*\"tools\".*})', t)
if not m:
    sys.exit(1)
d = json.loads(m.group(1))
print(len(d['result']['tools']))
")

echo "OK: initialize + tools/list — $count tools (session ${session:0:8}…)"
echo "$tools" | python3 -c "
import re, json, sys
t = sys.stdin.read()
m = re.search(r'data: ({.*\"tools\".*})', t)
for x in json.loads(m.group(1))['result']['tools']:
    print(' -', x['name'])
"
