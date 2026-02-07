#!/usr/bin/env python3
"""Regex Pattern Builder & Tester"""

import re

def test_pattern(text, pattern, flags=0):
    """Test regex pattern against text"""
    try:
        matches = re.findall(pattern, text, flags)
        search = re.search(pattern, text, flags)
        
        result = {
            "pattern": pattern,
            "text": text,
            "matches": matches,
            "match_count": len(matches)
        }
        
        if search:
            result["first_match"] = search.group()
            result["groups"] = search.groups()
        
        return result
    except re.error as e:
        return {"error": str(e)}

def generate_email_pattern():
    """Common email regex"""
    return r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def generate_phone_pattern():
    """Common phone regex"""
    return r'^(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'

def generate_url_pattern():
    """Common URL regex"""
    return r'https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'

if __name__ == "__main__":
    # Test email
    email_pattern = generate_email_pattern()
    result = test_pattern("john@example.com", email_pattern)
    print("Email test:", result)
