# JWT (JSON Web Tokens) Management

## JWT Structure

JWT consists of three Base64-encoded parts separated by dots:

```
header.payload.signature
```

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload
```json
{
  "sub": "user123",
  "email": "user@example.com",
  "iat": 1673865600,
  "exp": 1673869200
}
```

### Signature
```
HMACSHA256(base64(header) + "." + base64(payload), secret)
```

## JWT Best Practices

### 1. Use Short Expiration
- Access tokens: 15-60 minutes
- Refresh tokens: 7-30 days

### 2. Sign with Strong Secrets
```python
import os
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
assert len(SECRET_KEY) >= 32  # Minimum 32 bytes
```

### 3. Use HTTPS Only
Prevent token interception in transit

### 4. Validate Signature
Always verify signature before using token

```python
payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
```

### 5. Store Securely
- Server: Environment variable or secrets manager
- Client: HttpOnly cookie (not localStorage)

### 6. Implement Token Refresh
```
Send Access Token → Expires → Send Refresh Token → Get New Access Token
```

### 7. Add Claims Carefully
Only include necessary information in token (they're not encrypted, just signed)

## Verification Checklist

- [ ] Signature valid
- [ ] Token not expired
- [ ] Issuer is trusted
- [ ] Audience matches your service
- [ ] Required claims present
