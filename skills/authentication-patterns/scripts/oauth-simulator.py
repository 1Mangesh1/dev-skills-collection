#!/usr/bin/env python3
"""
OAuth Flow Simulator - Demonstrate OAuth 2.0 authorization code flow.
"""

import json
from typing import Dict
from urllib.parse import urlencode, parse_qs, urlparse

def generate_auth_request(client_id: str, redirect_uri: str, scope: str) -> str:
    """Generate OAuth2 authorization request URL."""
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scope,
        'state': 'random_state_value_123'
    }
    return f"https://auth-server.com/authorize?{urlencode(params)}"

def exchange_code_for_token(code: str, client_id: str, client_secret: str) -> Dict:
    """Simulate token exchange."""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "scope": "openid profile email"
    }

def validate_redirect_uri(redirect_uri: str, registered_uris: list) -> bool:
    """Validate redirect URI against registered URIs."""
    return redirect_uri in registered_uris

if __name__ == "__main__":
    req = generate_auth_request("client123", "https://app.example.com/callback", "openid profile")
    print(req)
