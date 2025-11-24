# How to Start ngrok for Twitter OAuth

## The Problem
Twitter OAuth is failing because **ngrok is not running**. Twitter needs to verify that the callback URL is reachable, and without ngrok, it can't.

## Solution: Start ngrok

### Step 1: Open a New Terminal Window
Keep this terminal open - ngrok must stay running while you test.

### Step 2: Start ngrok
```bash
cd /Users/consultadd/Desktop/Marketing
ngrok http 8000
```

### Step 3: Verify ngrok is Running
You should see output like:
```
Forwarding  https://unmonotonous-winnable-ashlee.ngrok-free.dev -> http://localhost:8000

Session Status                online
Account                       Your Account
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://unmonotonous-winnable-ashlee.ngrok-free.dev -> http://localhost:8000
```

### Step 4: Keep ngrok Running
**DO NOT CLOSE THIS TERMINAL** - ngrok must stay running for Twitter OAuth to work.

### Step 5: Test Twitter Connection
1. With ngrok running, try connecting Twitter again
2. Twitter should now be able to verify the callback URL
3. You should see the authorization page (not error page)

## Verify ngrok is Working

In another terminal, test:
```bash
curl http://localhost:4040/api/tunnels
```

You should see JSON with your ngrok URL.

## Important Notes

- ✅ ngrok must be running BEFORE you try to connect Twitter
- ✅ Keep the ngrok terminal window open
- ✅ The ngrok URL should match: `https://unmonotonous-winnable-ashlee.ngrok-free.dev`
- ✅ Make sure this URL is registered in Twitter Developer Portal

## If ngrok URL is Different

If ngrok gives you a different URL:
1. Copy the new ngrok URL
2. Update Twitter Developer Portal with the new callback URI
3. Update `.env` file: `TWITTER_REDIRECT_URI=https://NEW_NGROK_URL/oauth/twitter/callback`
4. Restart backend: `docker-compose restart backend`

