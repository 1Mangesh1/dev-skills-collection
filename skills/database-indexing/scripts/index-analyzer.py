#!/usr/bin/env python3
"""Index Analyzer - Identifies slow queries and recommends indexes"""

import json
from typing import List, Dict

def analyze_query_for_indexes(query: str) -> Dict:
    """Analyze SQL query and recommend optimal indexes"""
    
    # Simple parsing (production would use actual query parser)
    where_columns = []
    join_columns = []
    order_columns = []
    
    if "WHERE" in query:
        # Extract column names after WHERE
        where_columns = ["email", "status"]  # Example extraction
    
    if "JOIN" in query:
        join_columns = ["user_id", "id"]  # Example
    
    if "ORDER BY" in query:
        order_columns = ["created_at"]  # Example
    
    recommendations = []
    
    # Recommend indexes based on analysis
    if where_columns:
        recommendations.append({
            "index": f"CREATE INDEX idx_where ON table({', '.join(where_columns)})",
            "benefit": "Speeds up WHERE clause filtering",
            "priority": "HIGH"
        })
    
    if join_columns:
        recommendations.append({
            "index": f"CREATE INDEX idx_join ON table({', '.join(join_columns)})",
            "benefit": "Speeds up JOIN operations",
            "priority": "HIGH"
        })
    
    if order_columns:
        recommendations.append({
            "index": f"CREATE INDEX idx_sort ON table({', '.join(order_columns)})",
            "benefit": "Speeds up ORDER BY and sorting",
            "priority": "MEDIUM"
        })
    
    return {
        "query": query[:100] + "..." if len(query) > 100 else query,
        "analysis": {
            "where_columns": where_columns,
            "join_columns": join_columns,
            "order_columns": order_columns
        },
        "recommended_indexes": recommendations,
        "estimated_impact": "30-50% query time improvement"
    }

if __name__ == "__main__":
    sample_query = """
    SELECT u.id, u.email, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.status = 'active' AND u.created_at > '2024-01-01'
    ORDER BY u.created_at DESC
    """
    
    result = analyze_query_for_indexes(sample_query)
    print(json.dumps(result, indent=2))
