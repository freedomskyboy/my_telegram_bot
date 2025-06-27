# n8n on Render.com

Deploy [n8n](https://n8n.io) easily on [Render.com](https://render.com)

## 🔧 How to Use

1. Extract this zip and push it to a new GitHub repo
2. Go to [Render.com > New Web Service](https://dashboard.render.com/)
3. Connect to your GitHub repo
4. Choose:
   - Environment: Docker
   - Port: 5678
5. Add Environment Variables:
   - `N8N_BASIC_AUTH_USER`: admin
   - `N8N_BASIC_AUTH_PASSWORD`: admin123
   - `TELEGRAM_ACCESS_TOKEN`: your Telegram bot token

## ✅ Result

You’ll get a public URL like:

```
https://n8n-yourusername.onrender.com
```

Now you can use this URL for Telegram Webhooks.
