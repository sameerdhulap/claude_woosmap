# Deploy Woosmap MCP Server to Railway (for Web Claude)

This guide walks you through deploying the Woosmap MCP server to Railway.app so you can use it with web Claude.

## Prerequisites

- A [Railway.app](https://railway.app) account (free tier available)
- A Woosmap API key (get one at [console.woosmap.com](https://console.woosmap.com))
- The Woosmap skill files

## Step-by-Step Deployment

### 1. Prepare Your Files

Extract the `scripts/` folder from your `woosmap-skill.skill` file. You should have:

```
scripts/
├── server.py          # HTTP server (NEW - for web Claude)
├── main.py           # Original entry point
├── core.py
├── localities.py
├── distance.py
├── transit.py
├── exceptions.py
├── pyproject.toml
├── requirements.txt   # NEW - for Railway
├── Procfile          # NEW - for Heroku
└── railway.json      # NEW - for Railway config
```

### 2. Create a GitHub Repository (Recommended)

Railway works best with GitHub:

1. Create a new GitHub repository
2. Upload the `scripts/` folder contents to the root of the repo
3. Commit and push

**OR** you can deploy directly from your local machine using Railway CLI.

### 3. Deploy to Railway

#### Option A: Deploy from GitHub (Easiest)

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Python and deploy

#### Option B: Deploy from Local (Railway CLI)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Navigate to scripts folder
cd scripts/

# Initialize and deploy
railway init
railway up
```

### 4. Configure Environment Variables

1. In Railway dashboard, click on your deployment
2. Go to "Variables" tab
3. Add the following environment variable:
   - **Key**: `WOOSMAP_API_KEY`
   - **Value**: Your Woosmap API key

4. Save the variables

### 5. Get Your Server URL

1. In Railway dashboard, go to "Settings" tab
2. Under "Networking", click "Generate Domain"
3. Railway will give you a URL like: `https://woosmap-production.up.railway.app`
4. Copy this URL

### 6. Test Your Deployment

Visit your server URL in a browser:
```
https://your-app.up.railway.app/
```

You should see:
```json
{
  "service": "Woosmap MCP Server",
  "status": "running",
  "version": "1.0.0",
  "transport": "SSE"
}
```

### 7. Connect to Web Claude

1. Go to [claude.ai](https://claude.ai)
2. Open Settings → Integrations (or MCP Servers)
3. Click "Add MCP Server"
4. Configure:
   - **Name**: Woosmap
   - **URL**: `https://your-app.up.railway.app/sse`
   - **Type**: SSE (Server-Sent Events)
5. Save

### 8. Test in Web Claude

Start a new conversation and try:
- "Find coffee shops near Paris"
- "What's the distance from London to Edinburgh?"
- "Get directions from Times Square to Central Park"

## Costs

Railway offers:
- **Free Tier**: $5 credit per month (plenty for testing)
- **Hobby Plan**: $5/month for more usage
- **Pro Plan**: Pay as you go

Your Woosmap MCP server should use minimal resources and fit comfortably in the free tier for personal use.

## Troubleshooting

### Deployment fails

Check the build logs in Railway dashboard:
- Ensure `requirements.txt` is in the root
- Verify Python version compatibility

### Server starts but tools don't work in Claude

1. Check environment variables are set correctly
2. View logs in Railway: Dashboard → Deployments → View Logs
3. Verify the URL ends with `/sse`

### 500 Internal Server Error

- Check your Woosmap API key is valid
- View server logs in Railway dashboard
- Ensure you haven't exceeded Woosmap API quota

### CORS errors

- Verify the CORS middleware is configured correctly in `server.py`
- Check Railway logs for CORS-related errors

## Updating Your Deployment

To update your MCP server:

**Via GitHub:**
1. Push changes to your GitHub repo
2. Railway auto-deploys the new version

**Via Railway CLI:**
```bash
cd scripts/
railway up
```

## Monitoring

Railway provides:
- **Metrics**: CPU, memory, network usage
- **Logs**: Real-time server logs
- **Deployments**: History of all deployments

Check these regularly to ensure your server is healthy.

## Security Best Practices

1. **Never commit API keys** to GitHub
   - Always use environment variables
   - Add `.env` to `.gitignore`

2. **Limit CORS origins** in production
   - Only allow `claude.ai` domains
   - Remove localhost origins

3. **Monitor API usage**
   - Check Woosmap console for usage
   - Set up alerts for quota limits

## Alternative Hosting Options

If Railway doesn't work for you, try:
- **Render.com**: Similar to Railway, free tier available
- **Fly.io**: Good for global deployment
- **Google Cloud Run**: Generous free tier, scales to zero
- **Heroku**: Classic PaaS, uses the included `Procfile`

## Support

- **Railway Issues**: [railway.app/help](https://railway.app/help)
- **Woosmap API**: [developers.woosmap.com](https://developers.woosmap.com/)
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
