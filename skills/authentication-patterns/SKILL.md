---
name: authentication-patterns
description: Authentication and authorization patterns and best practices. Use when user asks to "implement authentication", "OAuth flow", "JWT tokens", "session management", "SSO setup", "API keys", "RBAC", "SAML", "passwordless auth", "multi-factor authentication", or mentions auth design patterns and security.
---

# Authentication & Authorization Patterns

Modern authentication and authorization patterns for web, mobile, and API applications.

## Authentication Methods

### OAuth 2.0
- Standard for third-party integrations
- Flows: Authorization Code, Implicit, Client Credentials, Resource Owner Password
- Popular providers: Google, GitHub, Facebook, Microsoft

### OpenID Connect (OIDC)
- Identity layer on top of OAuth 2.0
- Provides user information and authentication assurance

### JWT (JSON Web Tokens)
- Stateless token-based authentication
- Encrypted claims with signature
- Used for APIs and microservices

### Session-Based
- Traditional server-side session management
- Better for server-rendered applications
- Requires careful CSRF protection

### Passwordless
- Magic links via email
- WebAuthn/FIDO2
- Biometric authentication

## Authorization Patterns

### RBAC (Role-Based Access Control)
- User assigned to roles
- Roles have permissions
- Simple to implement and understand

### ABAC (Attribute-Based Access Control)
- Fine-grained permissions based on attributes
- More flexible but complex
- Good for complex permission requirements

### PBAC (Policy-Based Access Control)
- Permission as code (AWS IAM, Terraform)
- Highly flexible and auditable
- Supports delegation

## Security Best Practices

1. **Never store passwords** - Use bcrypt, scrypt, or Argon2
2. **Use HTTPS only** - All auth traffic encrypted
3. **Secure token storage** - HTTPOnly cookies for web
4. **Token rotation** - Regular refresh token rotation
5. **MFA/2FA** - Multi-factor authentication
6. **Audit logging** - Track all auth events
7. **Rate limiting** - Prevent brute force attacks
8. **CORS properly** - Restrict cross-origin access

## Common Architecture

```
Client → Auth Provider (OAuth/JWT) → API
Client → Session Store ← API
```

## References

- OAuth 2.0 Specification (RFC 6749)
- OpenID Connect Core
- JWT (RFC 7519)
- OWASP Authentication Cheat Sheet
- WebAuthn / FIDO2 Specification
