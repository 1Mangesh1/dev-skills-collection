# JWT vs Session Authentication

## JWT (JSON Web Tokens)

### Structure
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│ Header             │ Payload             │ Signature
```

### Pros
- ✓ Stateless (no server-side storage)
- ✓ Scalable (no session lookup)
- ✓ Works across domains
- ✓ Mobile-friendly

### Cons
- ✗ Can't revoke tokens easily
- ✗ Larger payload than session cookies
- ✗ XSS vulnerability if stored in localStorage

### Best For
- Single Page Applications (SPAs)
- Mobile applications
- Microservices
- API authentication

## Session-Based Authentication

### How It Works
```
1. User logs in with credentials
2. Server creates session, stores in memory/database
3. Returns session ID in HttpOnly cookie
4. Client sends cookie with each request
5. Server looks up session to verify user
```

### Pros
- ✓ Easy to revoke (delete session)
- ✓ Smaller cookie size
- ✓ Cannot be forged by client
- ✓ Built-in CSRF protection

### Cons
- ✗ Requires server-side storage
- ✗ Doesn't scale across multiple servers
- ✗ Requires session sharing (Redis)
- ✗ Doesn't work well for mobile

### Best For
- Traditional web applications
- Server-rendered apps
- Admin dashboards
- Apps with revocation needs

## Comparison Table

| Feature | JWT | Session |
|---------|-----|---------|
| Stateless | ✓ | ✗ |
| Revocable | ✗ | ✓ |
| Scalable | ✓ | (with Redis) |
| Server storage | ✗ | ✓ |
| CORS-friendly | ✓ | ✗ |
| Logout difficulty | Hard | Easy |
