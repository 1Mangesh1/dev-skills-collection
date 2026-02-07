# OAuth 2.0 Authorization Code Flow

## Step-by-Step Flow

```
1. User clicks "Login with Google"
   ↓
2. Redirect to Google (Authorization Server)
   GET https://accounts.google.com/o/oauth2/auth?
     client_id=YOUR_CLIENT_ID
     redirect_uri=https://yourapp.com/callback
     scope=openid+profile+email
     response_type=code
   ↓
3. User logs in and grants permission
   ↓
4. Google redirects back to your app with authorization code
   GET https://yourapp.com/callback?code=AUTH_CODE&state=xyz
   ↓
5. Your backend exchanges code for token
   POST https://accounts.google.com/o/oauth2/token
     code=AUTH_CODE
     client_id=YOUR_CLIENT_ID
     client_secret=YOUR_SECRET (keep secret!)
     grant_type=authorization_code
   ↓
6. Google returns access token
   {
     "access_token": "...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ↓
7. Use token to access protected resources
   GET https://www.googleapis.com/oauth2/v2/userinfo
   Authorization: Bearer ACCESS_TOKEN
```

## Key Security Elements

- **State parameter**: Prevents CSRF attacks
- **Client secret**: Kept on backend only
- **HTTPS only**: Prevents token interception
- **Token expiration**: Limits damage from compromised tokens
- **Refresh tokens**: Get new access tokens without re-login

## Popular Providers

- Google
- GitHub
- Microsoft
- Facebook
- Auth0
