# GraphQL Fundamentals

## Query vs Mutation

### Query (Read-only)
```graphql
query {
  user(login: "torvalds") {
    name
    bio
    repositories(first: 5) {
      totalCount
      nodes {
        name
        stargazers {
          totalCount
        }
      }
    }
  }
}
```

### Mutation (Write)
```graphql
mutation {
  createRepository(input: {
    name: "my-repo"
    description: "My repository"
    isPrivate: false
  }) {
    repository {
      id
      name
      url
    }
  }
}
```

## Response Structure

```json
{
  "data": {
    "user": {
      "name": "Linus Torvalds",
      "repositories": {
        "totalCount": 45,
        "nodes": [...]
      }
    }
  },
  "errors": []
}
```

## Fragments

Reuse query structure:

```graphql
fragment repositoryFields on Repository {
  name
  description
  stargazers {
    totalCount
  }
}

query {
  repository(owner: "angular", name: "angular") {
    ...repositoryFields
  }
}
```

## Variables

```graphql
query GetUser($login: String!) {
  user(login: $login) {
    name
    login
  }
}
```

Send with:
```json
{
  "variables": {
    "login": "torvalds"
  }
}
```

## Pagination

```graphql
query {
  user(login: "torvalds") {
    repositories(first: 10, after: "cursor") {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
      }
    }
  }
}
```

## Tools

- **GraphiQL** - Interactive IDE
- **Apollo DevTools** - Browser extension
- **Postman** - API testing
- **Insomnia** - REST/GraphQL client
