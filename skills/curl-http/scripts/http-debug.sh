#!/bin/bash
# HTTP Request Debugger - Debug and test HTTP requests with detailed output
# Usage: ./http-debug.sh [METHOD] URL [DATA]

set -e

METHOD="${1:-GET}"
URL="${2}"
DATA="${3}"

if [ -z "$URL" ]; then
    echo "Usage: $0 [METHOD] <URL> [DATA]"
    echo "Example: $0 GET https://api.example.com/users"
    echo "Example: $0 POST https://api.example.com/users '{\"name\":\"John\"}'"
    exit 1
fi

echo "==================== HTTP Request Debug ===================="
echo "Method: $METHOD"
echo "URL: $URL"
echo ""

# Extract components from URL
PROTOCOL=$(echo "$URL" | cut -d: -f1)
DOMAIN=$(echo "$URL" | sed 's|^[^:]*://||' | cut -d/ -f1)
PATH=$(echo "$URL" | sed 's|^[^:]*://[^/]*||')

echo "Protocol: $PROTOCOL"
echo "Domain: $DOMAIN"
echo "Path: ${PATH:-/}"
echo ""

# Resolve DNS
echo "==================== DNS Resolution ===================="
dig +short "$DOMAIN" | head -5

echo ""
echo "==================== HTTP Headers ===================="

# Build curl command
CURL_CMD="curl -i -X $METHOD"

if [ -n "$DATA" ]; then
    CURL_CMD="$CURL_CMD -d '$DATA' -H 'Content-Type: application/json'"
fi

# Add verbose output
CURL_CMD="$CURL_CMD -w '\n\nResponse Time: %{time_total}s\n' '$URL'"

echo "Command: $CURL_CMD"
echo ""
echo "==================== Response ===================="
eval "$CURL_CMD"
