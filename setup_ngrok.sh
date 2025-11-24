#!/bin/bash

echo "🚀 Starting ngrok tunnel for Twitter OAuth..."
echo ""
echo "This will create a public URL that tunnels to http://localhost:8000"
echo ""
echo "After ngrok starts, you'll see a URL like: https://abc123.ngrok.io"
echo ""
echo "Then update Twitter Developer Portal:"
echo "  - Callback URI: https://YOUR_NGROK_URL/oauth/twitter/callback"
echo ""
echo "Press Ctrl+C to stop ngrok when done"
echo ""
echo "Starting ngrok..."
echo ""

ngrok http 8000

