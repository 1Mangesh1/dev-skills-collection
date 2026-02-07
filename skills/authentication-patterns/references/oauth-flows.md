# OAuth 2.0 Flows Explained

## Authorization Code Flow (Recommended)

Used by web and mobile apps. Most secure for user delegation.

```
1. App → User: "Click login with Google"
2. User → Google: Enters credentials
3. Google → App: Redirects with authorization code
4. App Backend → Google: Exchanges code for token (with client secret)
5. Google → App: Returns access token
6. App → Google API: Uses access token
7. Google → App: Returns user data
```

**Best for:** Web apps, mobile apps
**Security:** Excellent (secret never exposed to user)

## Client Credentials Flow

Used for server-to-server authentication, no user involvement.

```
1. App Backend → Auth Server: client_id + client_secret
2. Auth Server → App: Returns access token
3. App → API: Uses token to access resources
```

**Best for:** Backend services, scheduled jobs
**Security:** Good (requires secure client secret storage)

## Implicit Flow (Legacy - Don't Use)

```
1. App → Auth Server: client_id + redirect_uri
2. Auth Server → Browser: Returns token in URL
3. Browser → App: Token accessible to JavaScript
```

**Problems:** Token visible in browser history, vulnerable to XSS

## Resource Owner Password Flow (Legacy)

```
1. App → Auth Server: username + password + client_id
2. Auth Server → App: Returns access token
```

**Only use:** Legacy systems, trusted apps
**Never use:** Third-party apps

## OpenID Connect (OIDC)

OpenID Connect is an identity layer on top of OAuth 2.0. It provides:
- User identification (ID token)
- User information (userinfo endpoint)
- Authentication assurance

**ID Token structure:**
```json
{
  "iss": "https://accounts.google.com",
  "sub": "110169547927130675053",
  "name": "John Doe",
  "email": "john@example.com",
  "aud": "your-client-id.apps.googleusercontent.com"
}
```

## Token Refresh Pattern

```
Access Token (short-lived): 1 hour
Refresh Token (long-lived): 30 days

When access token expires:
1. Client sends refresh token
2. Auth Server validates and returns new access token
3. If refresh token also expired, user must login again
```

## Security Considerations

1. **Token Storage**: Use secure, HTTPOnly cookies (not localStorage)
2. **HTTPS Only**: Always use HTTPS for auth flows
3. **CSRF**: Include CSRF tokens for form-based auth
4. **State Parameter**: Prevent CSRF in OAuth flows
5. **Scope Limitation**: Request minimal necessary scopes
6. **Token Rotation**: Rotate tokens regularly
7. **PKCE**: Use for mobile/SPA apps (prevents authorization code interception)
