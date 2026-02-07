# GraphQL Best Practices

## Query Optimization

### ❌ Over-fetching
```graphql
query {
  user {
    id
    name
    email
    birthDate  # Not needed
    address    # Not needed
  }
}
```

### ✓ Precise Query
```graphql
query {
  user {
    id
    name
    email
  }
}
```

## Error Handling

```graphql
query {
  user(login: "invalid") {
    name
  }
}
```

Response:
```json
{
  "data": {
    "user": null
  },
  "errors": [
    {
      "message": "Could not resolve user with login \"invalid\"",
      "locations": [{"line": 1, "column": 2}]
    }
  ]
}
```

## Rate Limiting

GitHub GraphQL API:
- Calculated points per query (varying complexity)
- 5,000 points per hour
- Check with `rateLimit` query:

```graphql
query {
  rateLimit {
    limit
    remaining
    resetAt
  }
}
```

## Performance Tips

1. **Use aliases for same query**:
```graphql
query {
  pytorch: repository(owner: "pytorch", name: "pytorch") {
    stargazers { totalCount }
  }
  tensorflow: repository(owner: "tensorflow", name: "tensorflow") {
    stargazers { totalCount }
  }
}
```

2. **Batch queries**: Request multiple resources in one query

3. **Use datetime formats**: ISO8601 format

4. **Implement pagination**: Don't fetch everything

## Security

```graphql
# ❌ Never expose secrets
mutation {
  createSecret(value: "sk_live_abc123xyz")
}

# ✓ Use authentication tokens
# Authenticate like: Authorization: Bearer token
```
