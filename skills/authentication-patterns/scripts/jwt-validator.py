#!/usr/bin/env python3
"""
JWT Token Validator - Validate and decode JWT tokens.
Useful for testing authentication implementations.
"""

import json
import base64
from typing import Dict, Tuple

def decode_jwt(token: str) -> Dict:
    """Decode JWT token (without validation)."""
    parts = token.split('.')
    if len(parts) != 3:
        return {"error": "Invalid JWT format"}
    
    # Decode payload
    payload = parts[1]
    # Add padding if needed
    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += '=' * padding
    
    try:
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {"error": str(e)}

def validate_token_claims(token_payload: Dict, required_claims: list) -> Tuple[bool, list]:
    """Validate that token has required claims."""
    missing = [claim for claim in required_claims if claim not in token_payload]
    return len(missing) == 0, missing

def check_token_expiration(token_payload: Dict) -> bool:
    """Check if token has expired."""
    import time
    exp = token_payload.get('exp')
    if not exp:
        return False
    return time.time() < exp

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(json.dumps(decode_jwt(token), indent=2))
