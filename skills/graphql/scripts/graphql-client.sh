#!/usr/bin/env bash
# GraphQL Query Tool
# Common GraphQL queries and mutations

execute_graphql() {
    local query="$1"
    local endpoint="${2:-https://api.github.com/graphql}"
    local token="$GITHUB_TOKEN"
    
    curl -s -X POST "$endpoint" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{\"query\":\"$query\"}" | jq '.'
}

get_user_info() {
    local username="$1"
    
    query='query {
      user(login: "'$username'") {
        name
        login
        repositories(first: 5) {
          totalCount
          nodes {
            name
            description
          }
        }
      }
    }'
    
    execute_graphql "$query"
}

# Usage
get_user_info "torvalds"
