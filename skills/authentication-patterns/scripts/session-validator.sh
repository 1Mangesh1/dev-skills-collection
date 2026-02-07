#!/bin/bash
# Session Security Validator - Check session configuration

check_session_cookies() {
    echo "Checking session cookie security..."
    echo ""
    echo "Required attributes:"
    echo "✓ HttpOnly - Prevents JavaScript access"
    echo "✓ Secure - Only sent over HTTPS"
    echo "✓ SameSite - Prevents CSRF (Strict/Lax)"
    echo "✓ Path - Limited scope"
    echo "✓ Domain - Correct domain"
    echo "✓ MaxAge/Expires - Reasonable timeout"
}

check_token_storage() {
    echo "Token Storage recommendations:"
    echo "- localStorage: ✗ Vulnerable to XSS"
    echo "- sessionStorage: ✗ Vulnerable to XSS"
    echo "- Memory: ✓ CSRF safe, cleared on refresh"
    echo "- HTTPOnly Cookie: ✓ CSRF token needed, XSS safe"
}

case "$1" in
    cookies)
        check_session_cookies
        ;;
    storage)
        check_token_storage
        ;;
    *)
        check_session_cookies
        echo ""
        check_token_storage
        ;;
esac
