---
name: authentication-patterns
description: Comprehensive authentication and authorization implementation guide. Use when the user asks about JWT tokens, OAuth 2.0 flows, session management, API key auth, SSO setup, SAML, OIDC, password hashing, multi-factor authentication, CSRF protection, token storage, CORS headers, rate limiting auth endpoints, or auth middleware patterns.
---

# Authentication and Authorization Patterns

Reference for implementing authentication in web, mobile, and API applications.

---

## 1. JWT (JSON Web Tokens)

### Structure

Three Base64URL-encoded parts separated by dots: `header.payload.signature`.

- **Header** -- algorithm (`alg`) and token type (`typ`).
- **Payload** -- claims: `sub`, `iat`, `exp`, `iss`, `aud`, plus custom claims.
- **Signature** -- HMAC-SHA256 or RSA/ECDSA over header and payload.

### Signing

- **Symmetric (HS256)** -- shared secret; simple but the secret must live on every verifier.
- **Asymmetric (RS256, ES256)** -- private key signs, public key verifies. Publish via JWKS endpoint.

### Access + Refresh Token Flow

1. Client authenticates. Server returns a short-lived access token (5-15 min) and a long-lived refresh token.
2. Client sends `Authorization: Bearer <access_token>` on each request.
3. On expiry, client posts the refresh token to a dedicated endpoint to get a new access token.
4. Server optionally rotates the refresh token on each use. If revoked/expired, user re-authenticates.

### JWT Example (Node.js)

```js
const jwt = require("jsonwebtoken");
const accessToken = jwt.sign({ sub: user.id, role: user.role }, process.env.JWT_SECRET, { expiresIn: "15m" });
const refreshToken = jwt.sign({ sub: user.id }, process.env.REFRESH_SECRET, { expiresIn: "7d" });

function verifyToken(req, res, next) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) return res.sendStatus(401);
  try { req.user = jwt.verify(header.slice(7), process.env.JWT_SECRET); next(); }
  catch { return res.sendStatus(401); }
}
```

### JWT Pitfalls

- JWTs are encoded, not encrypted -- never put secrets in claims.
- Always validate `exp`, `iss`, and `aud` on the server.
- Enforce the expected algorithm to prevent `alg: none` or algorithm-switching attacks.

---

## 2. OAuth 2.0 Flows

### Authorization Code Flow

For server-side apps. Client gets an authorization code via redirect and exchanges it for tokens server-side.

1. Redirect to `GET /authorize?response_type=code&client_id=...&redirect_uri=...&scope=...&state=...`
2. User authenticates and consents. Auth server redirects with `?code=...&state=...`
3. Server exchanges the code: `POST /token` with `grant_type=authorization_code`, code, client_id, client_secret.

### Authorization Code with PKCE

Required for public clients (SPAs, mobile) that cannot store a client secret.

- Generate random `code_verifier`, derive `code_challenge = BASE64URL(SHA256(code_verifier))`.
- Send `code_challenge` and `code_challenge_method=S256` in the authorize request.
- Send `code_verifier` in the token exchange. Server verifies the hash matches.

### Client Credentials Flow

Machine-to-machine, no user. `POST /token` with `grant_type=client_credentials`, client_id, client_secret, scope. Returns an access token directly.

### Device Authorization Flow

For input-constrained devices (smart TVs, CLI tools). Device gets a user code and verification URL, user authenticates on another device, device polls until complete.

### OAuth Example (Python)

```python
import requests
resp = requests.post("https://auth.example.com/token", data={
    "grant_type": "authorization_code", "code": auth_code,
    "redirect_uri": REDIRECT_URI, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
})
access_token = resp.json()["access_token"]
data = requests.get("https://api.example.com/data",
    headers={"Authorization": f"Bearer {access_token}"}).json()
```

---

## 3. Session-Based Authentication

1. User submits credentials. Server creates a session, stores it (memory/Redis/database), returns a session ID cookie.
2. Browser sends the cookie automatically. Server looks up the session to identify the user.

### Cookie Configuration

```
Set-Cookie: sid=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
```

- **HttpOnly** -- not accessible to JavaScript. **Secure** -- HTTPS only. **SameSite** -- mitigates CSRF.

### Session Stores

| Store    | Pros                         | Cons                            |
|----------|------------------------------|---------------------------------|
| Memory   | Zero setup                   | Lost on restart, single-process |
| Redis    | Fast, TTL support, clustered | Extra infrastructure            |
| Database | Durable, queryable           | Slower, needs cleanup job       |

### Sliding vs. Absolute Expiration

- **Absolute** -- expires at a fixed time. **Sliding** -- resets on each request. Combine both: slide 30 min with an 8-hour hard cap.

---

## 4. API Key Authentication

- **Generate** with a CSPRNG (`crypto.randomBytes(32)`, `secrets.token_urlsafe(32)`). Prefix for identification: `sk_live_...`.
- **Store** hashed (SHA-256) in the database. Show the raw key to the user once at creation.
- **Rotate** by allowing a new key before revoking the old one; support an overlap period.
- Best for server-to-server calls and usage tracking. Not suitable as sole auth for user-facing apps.

---

## 5. Basic Authentication

`Authorization: Basic base64(username:password)`

**Acceptable**: internal services behind VPN over TLS, development environments, webhook shared secrets.
**Not acceptable**: public-facing APIs, anything without HTTPS, anywhere token-based auth is feasible. Always pair with rate limiting.

---

## 6. Multi-Factor Authentication

### TOTP (Time-Based One-Time Passwords)

- Shared secret provisioned via QR code (`otpauth://` URI). Client generates a 6-digit code every 30 seconds.
- Server accepts current step +/- 1 for clock skew. Libraries: `pyotp`, `speakeasy`.

### WebAuthn / Passkeys

- Phishing-resistant: credential is bound to the origin by the browser.
- Registration: server sends challenge, authenticator creates key pair, public key stored server-side.
- Authentication: server sends challenge, authenticator signs it, server verifies.
- Passkeys sync across devices via platform credential managers.

### Guidance

- Offer hashed backup codes. Store MFA secrets encrypted at rest.
- Do not reveal MFA status during login -- check password first, then prompt for second factor.

---

## 7. Single Sign-On (SSO)

### SAML 2.0

- XML-based, common in enterprise. SP redirects to IdP, IdP posts a signed assertion to the SP's ACS URL.
- Validate signature, audience, timestamps, and InResponseTo on every assertion.

### OpenID Connect (OIDC)

- Identity layer on OAuth 2.0. Authorization Code flow returns an `id_token` (JWT) with user claims (`sub`, `email`, `name`).
- Discovery at `/.well-known/openid-configuration`. Verify `id_token` via JWKS; validate `iss`, `aud`, `exp`, `nonce`.

### Choosing

- OIDC: simpler, JSON-based, better for modern apps. SAML: entrenched in enterprise; support when customers require it.

---

## 8. Password Hashing

| Algorithm | Notes                                                    |
|-----------|----------------------------------------------------------|
| bcrypt    | Widely supported, cost factor 12+ recommended            |
| Argon2id  | Password Hashing Competition winner, memory-hard         |
| scrypt    | Memory-hard, good where Argon2 is unavailable            |

**Never use** MD5, SHA-1, or SHA-256 alone -- these are fast hashes, trivially brute-forced. Never use unsalted hashes.

```python
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
is_valid = bcrypt.checkpw(password.encode(), hashed)
```

---

## 9. Token Storage in the Browser

| Method          | XSS Risk | CSRF Risk | Notes                                           |
|-----------------|----------|-----------|-------------------------------------------------|
| httpOnly cookie | Low      | Medium    | Not accessible to JS; pair with SameSite + CSRF |
| localStorage    | High     | None      | Readable by any script on the page              |
| sessionStorage  | High     | None      | Clears on tab close                             |
| In-memory (JS)  | Low      | None      | Lost on refresh; use silent refresh flow         |

**Recommended**: refresh tokens in httpOnly Secure SameSite cookies; access tokens in memory; silent refresh on page load.

---

## 10. CORS and Authentication Headers

- Use specific origins (not `*`) with `Access-Control-Allow-Credentials: true`.
- Include `Authorization` in `Access-Control-Allow-Headers`.
- Keep allowed origins in server config, not hardcoded.

---

## 11. Rate Limiting for Auth Endpoints

- Strict limits on `/login`, `/token`, `/register`, `/password-reset`.
- Rate limit by both IP and account to counter credential stuffing.
- Return `429 Too Many Requests` with `Retry-After`. Use exponential backoff lockouts.
- Separate auth rate limits from general API limits.

---

## 12. Common Vulnerabilities

- **Token leakage** -- tokens in query strings get logged and leaked via referrer headers. Send in headers or POST bodies. Mask tokens in logs.
- **Session fixation** -- attacker sets a session ID before login. Mitigate by regenerating the session ID on authentication.
- **CSRF** -- browser sends cookies automatically. Mitigate with SameSite cookies, anti-CSRF tokens, and Origin/Referer verification.
- **Credential stuffing** -- breached password lists. Mitigate with rate limiting, MFA, and breach-detection APIs.
- **JWT algorithm confusion** -- enforce the expected algorithm server-side; reject `alg: none`.
- **Open redirects in OAuth** -- validate `redirect_uri` matches a pre-registered value exactly.

---

## 13. Auth Middleware Patterns

### Express (Node.js)

```js
function requireAuth(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Missing token" });
  try { req.user = jwt.verify(token, process.env.JWT_SECRET); next(); }
  catch { return res.status(401).json({ error: "Invalid token" }); }
}
function requireRole(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) return res.status(403).json({ error: "Forbidden" });
    next();
  };
}
app.get("/admin", requireAuth, requireRole("admin"), adminHandler);
```

### FastAPI (Python)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = await get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

@app.get("/profile")
async def profile(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
```

### Next.js (Middleware)

```ts
import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";
const SECRET = new TextEncoder().encode(process.env.JWT_SECRET);

export async function middleware(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value;
  if (!token) return NextResponse.redirect(new URL("/login", request.url));
  try { await jwtVerify(token, SECRET); return NextResponse.next(); }
  catch { return NextResponse.redirect(new URL("/login", request.url)); }
}
export const config = { matcher: ["/dashboard/:path*", "/api/protected/:path*"] };
```

---

## References

- RFC 6749 -- OAuth 2.0 Authorization Framework
- RFC 7519 -- JSON Web Token
- RFC 7636 -- Proof Key for Code Exchange (PKCE)
- RFC 8628 -- Device Authorization Grant
- OpenID Connect Core 1.0
- OWASP Authentication Cheat Sheet
- OWASP Session Management Cheat Sheet
- WebAuthn (W3C)
- NIST SP 800-63B -- Digital Identity Guidelines
