# 🔗 OAuth Setup Guide for Social Media Platforms

This guide will help you set up OAuth authentication for connecting social media platforms to your AI Content Generator application.

## 📋 Prerequisites

- Developer accounts on the platforms you want to connect
- Valid domain/URL for OAuth redirects
- Backend server running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`

## 🐦 Twitter (X) OAuth Setup

### 1. Create Twitter App
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use existing one
3. Navigate to "App Settings" → "User authentication settings"
4. Enable OAuth 2.0
5. Set App permissions to "Read and Write"
6. Add callback URLs:
   - `http://localhost:8000/oauth/twitter/callback` (for development)
   - `https://yourdomain.com/oauth/twitter/callback` (for production)

### 2. Get Credentials
- **Client ID**: Found in your app's "Keys and tokens" section
- **Client Secret**: Found in your app's "Keys and tokens" section

### 3. Environment Variables
```bash
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
```

## 📘 LinkedIn OAuth Setup

### 1. Create LinkedIn App
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create a new app
3. Go to "Auth" tab
4. Add OAuth 2.0 redirect URLs:
   - `http://localhost:8000/oauth/linkedin/callback` (for development)
   - `https://yourdomain.com/oauth/linkedin/callback` (for production)

### 2. Get Credentials
- **Client ID**: Found in your app's "Auth" tab
- **Client Secret**: Found in your app's "Auth" tab

### 3. Environment Variables
```bash
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

## 📘 Facebook OAuth Setup

### 1. Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Go to "Facebook Login" → "Settings"
4. Add OAuth redirect URIs:
   - `http://localhost:8000/oauth/facebook/callback` (for development)
   - `https://yourdomain.com/oauth/facebook/callback` (for production)

### 2. Get Credentials
- **App ID**: Found in your app's "Settings" → "Basic"
- **App Secret**: Found in your app's "Settings" → "Basic"

### 3. Environment Variables
```bash
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

## 📷 Instagram OAuth Setup

### 1. Create Instagram App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app (or use existing Facebook app)
3. Add "Instagram Basic Display" product
4. Go to "Instagram Basic Display" → "Basic Display"
5. Add OAuth redirect URIs:
   - `http://localhost:8000/oauth/instagram/callback` (for development)
   - `https://yourdomain.com/oauth/instagram/callback` (for production)

### 2. Get Credentials
- **App ID**: Same as Facebook app ID
- **App Secret**: Same as Facebook app secret

### 3. Environment Variables
```bash
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret
```

## 📧 Email Setup (SendGrid)

### 1. Create SendGrid Account
1. Go to [SendGrid](https://sendgrid.com/)
2. Create an account and verify your domain
3. Generate an API key with "Mail Send" permissions

### 2. Environment Variables
```bash
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

## 🚀 Complete Environment Setup

Copy this to your `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/content_generator
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=content_generator

# Backend Configuration
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Twitter OAuth
TWITTER_CLIENT_ID=your-twitter-client-id
TWITTER_CLIENT_SECRET=your-twitter-client-secret

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Facebook OAuth
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# Instagram OAuth
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret

# Email Configuration (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

## 🔧 Testing OAuth Flow

### 1. Start Your Application
```bash
# Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm start
```

### 2. Test Connection Flow
1. Login to your application
2. Go to Profile page
3. Click "Connect" on any social media platform
4. You should be redirected to the platform's OAuth page
5. Authorize the application
6. You should be redirected back with a success message

## 🚨 Common Issues & Solutions

### Issue: "Invalid redirect URI"
**Solution**: Ensure the redirect URI in your OAuth app settings exactly matches what's in your code.

### Issue: "Client ID not found"
**Solution**: Check that your environment variables are properly set and the backend is restarted.

### Issue: "OAuth callback not working"
**Solution**: Verify that your callback endpoint is accessible and the redirect URL is correct.

### Issue: "Token exchange failed"
**Solution**: Check that your client secret is correct and the OAuth app has the right permissions.

## 🔒 Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Implement proper state validation** in production
4. **Use HTTPS** in production for all OAuth flows
5. **Regularly rotate** your client secrets
6. **Monitor OAuth usage** for suspicious activity

## 📚 Additional Resources

- [Twitter OAuth 2.0 Documentation](https://developer.twitter.com/en/docs/authentication/oauth-2-0)
- [LinkedIn OAuth Documentation](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Facebook OAuth Documentation](https://developers.facebook.com/docs/facebook-login)
- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)

## 🎯 Next Steps

After setting up OAuth:

1. **Test all connections** to ensure they work properly
2. **Implement token refresh** logic for expired tokens
3. **Add error handling** for failed connections
4. **Implement webhook handling** for real-time updates
5. **Add analytics** to track connection success rates

---

**Need Help?** Check the backend logs for detailed error messages and ensure all environment variables are properly set.
