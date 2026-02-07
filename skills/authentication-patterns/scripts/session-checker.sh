#!/usr/bin/env bash
# Session Configuration Checker
# Validates secure session cookie settings

check_session_security() {
    local cookie_config="$1"
    
    echo "=== Secure Session Checklist ==="
    echo ""
    
    [[ "$cookie_config" == *"HttpOnly"* ]] && echo "✓ HttpOnly flag set" || echo "✗ Missing HttpOnly flag"
    [[ "$cookie_config" == *"Secure"* ]] && echo "✓ Secure flag set (HTTPS only)" || echo "✗ Missing Secure flag"
    [[ "$cookie_config" == *"SameSite"* ]] && echo "✓ SameSite attribute set" || echo "✗ Missing SameSite attribute"
    
    echo ""
    echo "Recommended configuration:"
    echo "Set-Cookie: sessionId=abc123; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=3600"
}

check_session_security "HttpOnly; Secure; SameSite=Strict"
