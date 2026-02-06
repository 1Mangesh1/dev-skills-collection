# Authentication Patterns Quick Start

Implement secure authentication and authorization for modern applications.

## Quick Decision Tree

```
Authenticating Users?
├─ Web App (Server-rendered) → Session-based
├─ SPA (React/Vue) → JWT or Session + HTTPOnly
├─ Mobile App → OAuth 2.0 + JWT
└─ API → API Key or JWT
```

## Common Flows

### OAuth 2.0 Authorization Code
```
1. User clicks "Login with Google"
2. Redirects to Google login
3. Google redirects back with authorization code
4. Backend exchanges code for access token
5. Backend stores token, sets session
```

### JWT Token Flow
```
1. Login endpoint returns JWT
2. Client stores JWT (localStorage)
3. Client sends JWT in Authorization header
4. Server validates JWT signature
5. Request allowed if token valid
```

## Security Checklist

- [ ] Use HTTPS only
- [ ] MFA enabled for sensitive operations
- [ ] Tokens have expiration times
- [ ] Refresh tokens for extending sessions
- [ ] Secure cookie settings (HTTPOnly, SameSite)
- [ ] CORS properly configured

## Common Standards

| Standard | Use Case |
|----------|----------|
| OAuth 2.0 | Third-party login (Google, GitHub, etc.) |
| OpenID Connect | Authentication + user info |
| JWT | Stateless API authentication |
| SAML | Enterprise SSO |
| Session | Traditional web apps |

## Tools & Libraries

- Auth0, Okta, Cognito (managed)
- Passport.js, express-session (Node)
- django-allauth, Django Ninja (Python)
- Firebase Auth (quick setup)

## Resources

- [OAuth 2.0 Spec](https://tools.ietf.org/html/rfc6749)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)
- [OWASP Auth Cheat Sheet](https://cheatsheetseries.owasp.org/)

## See Also

- SKILL.md - Detailed patterns with code examples
- metadata.json - Official documentation links
