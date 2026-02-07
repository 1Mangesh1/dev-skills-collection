#!/usr/bin/env python3
"""
Query Analyzer - Analyze SQL queries for index opportunities.
Identifies slow queries and suggests indexes.
"""

import json
import re
from typing import List, Dict

def analyze_query(query: str) -> Dict:
    """Analyze SQL query for optimization opportunities."""
    analysis = {
        "query": query,
        "type": identify_query_type(query),
        "tables": extract_tables(query),
        "where_columns": extract_where_columns(query),
        "join_columns": extract_join_columns(query),
        "order_by_columns": extract_order_by_columns(query),
        "suggested_indexes": generate_index_suggestions(query),
        "complexity": estimate_complexity(query)
    }
    return analysis

def identify_query_type(query: str) -> str:
    """Identify if SELECT, INSERT, UPDATE, DELETE."""
    query = query.strip().upper()
    for query_type in ["SELECT", "INSERT", "UPDATE", "DELETE"]:
        if query.startswith(query_type):
            return query_type
    return "UNKNOWN"

def extract_tables(query: str) -> List[str]:
    """Extract table names from query."""
    # Simple regex - in production use SQL parser
    pattern = r'FROM\s+(\w+)|JOIN\s+(\w+)'
    matches = re.findall(pattern, query, re.IGNORECASE)
    return [m[0] or m[1] for m in matches]

def extract_where_columns(query: str) -> List[str]:
    """Extract columns used in WHERE clause."""
    pattern = r'WHERE\s+(\w+)\s*[=<>]'
    return re.findall(pattern, query, re.IGNORECASE)

def extract_join_columns(query: str) -> List[str]:
    """Extract columns used in JOINs."""
    pattern = r'ON\s+(\w+)\s*[=<>]\s*(\w+)'
    matches = re.findall(pattern, query, re.IGNORECASE)
    return [item for pair in matches for item in pair]

def extract_order_by_columns(query: str) -> List[str]:
    """Extract columns in ORDER BY."""
    pattern = r'ORDER\s+BY\s+(\w+)'
    return re.findall(pattern, query, re.IGNORECASE)

def generate_index_suggestions(query: str) -> List[str]:
    """Generate index recommendations."""
    suggestions = []
    where_cols = extract_where_columns(query)
    join_cols = extract_join_columns(query)
    order_cols = extract_order_by_columns(query)
    
    if where_cols:
        suggestions.append(f"CREATE INDEX idx_where ON table({','.join(where_cols)})")
    if join_cols:
        suggestions.append(f"CREATE INDEX idx_join ON table({','.join(join_cols)})")
    if order_cols:
        suggestions.append(f"CREATE INDEX idx_order ON table({','.join(order_cols)})")
    
    return suggestions

def estimate_complexity(query: str) -> str:
    """Estimate query complexity."""
    join_count = query.upper().count('JOIN')
    where_count = len(extract_where_columns(query))
    
    if join_count > 3 or where_count > 5:
        return "HIGH"
    elif join_count > 1 or where_count > 2:
        return "MEDIUM"
    else:
        return "LOW"

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "SELECT * FROM users WHERE age > 18"
    result = analyze_query(query)
    print(json.dumps(result, indent=2))
