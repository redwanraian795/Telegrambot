# Render Deployment Guide

## Files to Upload to GitHub

### Core Files (Required)
```
main.py
bot_handlers.py
ai_services.py
config.py
utils.py
bot_manager.py
keep_alive.py
multi_keep_alive.py
app.py
server.py
web_server.py
run.py
```

### Service Files (Required)
```
accessibility_service.py
admin_controls_service.py
advanced_ai_service.py
advanced_content_service.py
ai_agent_automation_service.py
animation_service.py
blockchain_web3_service.py
character_customization_service.py
content_generation_service.py
contextual_help_service.py
enhanced_vision_service.py
financial_tools.py
games_service.py
group_settings.py
group_surveillance_service.py
image_analysis_service.py
language_service.py
memory_service.py
null_safety_utils.py
professional_tools_service.py
public_api_service.py
realtime_service.py
scheduling_service.py
smart_home_service.py
social_monitoring_service.py
user_access_service.py
voice_service.py
```

### Configuration Files (Required)
```
requirements_render.txt  (rename to requirements.txt)
Procfile_render         (rename to Procfile)
render.yaml
runtime.txt
.env.example
.gitignore
README.md
```

### Documentation Files (Optional)
```
FREE_24_7_SETUP.md
GROUP_FEATURES_GUIDE.md
GROUP_MODERATION_GUIDE.md
USER_FEATURES_GUIDE.md
USER_PERMISSIONS_GUIDE.md
DEPLOYMENT_GUIDE.md
```

## Step-by-Step Deployment

### 1. Prepare GitHub Repository

1. Create new repository on GitHub
2. Upload all files listed above
3. **Important**: Rename files:
   - `requirements_render.txt` → `requirements.txt`
   - `Procfile_render` → `Procfile`

### 2. Set Up Render

1. Go to [render.com](https://render.com)
2. Sign up/login with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure deployment:
   - **Name**: telegram-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free

### 3. Environment Variables

Add these in Render dashboard:

**Required:**
```
TELEGRAM_TOKEN=your_telegram_bot_token
ADMIN_USER_ID=your_telegram_user_id
GEMINI_API_KEY=your_gemini_api_key
```

**Optional:**
```
OPENAI_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=your_secret_key
SESSION_SECRET=your_session_secret
PORT=10000
```

### 4. Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your bot will be live at: `https://your-app-name.onrender.com`

## Troubleshooting

### Common Issues

1. **Build Fails**: Check requirements.txt formatting
2. **Bot Not Responding**: Verify TELEGRAM_TOKEN
3. **AI Not Working**: Check GEMINI_API_KEY
4. **Port Issues**: Render uses port 10000 by default

### Logs

View deployment logs in Render dashboard:
- Go to your service
- Click "Logs" tab
- Monitor for errors

### Testing

1. Send `/start` to your bot
2. Try `/help` command
3. Test AI chat functionality
4. Verify admin commands work

## Free Tier Limitations

- 500 hours/month
- Sleeps after 15 minutes of inactivity
- Automatic wake-up on requests
- No custom domains

## Production Recommendations

For heavy usage, consider:
- Paid Render plan ($7/month)
- Enable auto-deploy from GitHub
- Set up monitoring
- Configure custom domain

---

Your bot will be running 24/7 on Render's free tier with automatic wake-up when users interact with it.