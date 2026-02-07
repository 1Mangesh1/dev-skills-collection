#!/usr/bin/env python3
"""GraphQL Schema Introspection Tool"""

import requests
import json

def introspect_schema(endpoint, headers=None):
    """Get GraphQL schema information"""
    
    introspection_query = """
    query IntrospectionQuery {
      __schema {
        types {
          name
          kind
          description
          fields {
            name
            type { name }
          }
        }
      }
    }
    """
    
    response = requests.post(
        endpoint,
        json={"query": introspection_query},
        headers=headers or {}
    )
    
    return response.json()

def list_queries(schema_data):
    """Extract available queries"""
    schema = schema_data.get('data', {}).get('__schema', {})
    
    query_type = next(
        (t for t in schema.get('types', []) if t['name'] == 'Query'),
        None
    )
    
    if query_type:
        print("Available Queries:")
        for field in query_type.get('fields', []):
            print(f"  - {field['name']}")

if __name__ == "__main__":
    endpoint = "https://api.github.com/graphql"
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    
    schema = introspect_schema(endpoint, headers)
    list_queries(schema)
