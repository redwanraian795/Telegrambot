# Advanced AI Telegram Bot

A comprehensive Telegram bot with advanced AI capabilities, offering intelligent and comprehensive user experiences through dynamic service integrations, multi-platform connectors, and adaptive interaction technologies.

## Features

### Core AI Services
- **Multi AI Integration**: Google Gemini Pro and OpenAI GPT-4o support  
- **Intelligent Chat**: Context-aware conversations with personality adaptation
- **Educational Support**: Math, science, coding, and creative writing assistance
- **Wikipedia Integration**: Quick information lookup and research

### Advanced Capabilities  
- **Accessibility Features**: Text-to-speech, high-contrast formatting, screen reader support
- **Cryptocurrency Tracking**: Real-time prices, predictions, portfolio management, price alerts
- **Games & Entertainment**: Trivia, word games, memes, stories, workouts, recipes
- **Memory System**: Conversation context, user preferences, personality profiles
- **Vision Analysis**: Image understanding, OCR, facial recognition, scene analysis

### Group Management
- **Admin Controls**: Comprehensive moderation tools and spam detection
- **Surveillance System**: Complete activity logging and member monitoring  
- **Settings Management**: Per-group feature configuration
- **User Access Control**: Multi-tier permission system (basic, premium, VIP, admin)

### Professional Tools
- **Content Generation**: Custom memes, stories, workout plans, recipes
- **Multi-Agent AI**: Research, content creation, data analysis, project management
- **Smart Calendar**: Intelligent scheduling with conflict resolution
- **Personal AI Coach**: Goal tracking, habit formation, progress analytics

## Technology Stack

- **Framework**: Python with python-telegram-bot library
- **AI Services**: Google Gemini Pro, OpenAI GPT-4o
- **Web Framework**: Flask with Gunicorn for production
- **Data Storage**: JSON-based persistence with PostgreSQL support
- **Media Processing**: PIL, pydub, speech recognition
- **Translation**: Google Translate API with 16+ language support

## Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Google Gemini API Key
- Optional: OpenAI API Key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/telegram-bot.git
cd telegram-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the bot:
```bash
python main.py
```

## Environment Variables

### Required
```env
TELEGRAM_TOKEN=your_telegram_bot_token
ADMIN_USER_ID=your_telegram_user_id
GEMINI_API_KEY=your_gemini_api_key
```

### Optional
```env
OPENAI_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=your_secret_key
SESSION_SECRET=your_session_secret
```

## Deployment

### Render Deployment

1. Fork this repository to your GitHub account
2. Connect your GitHub repo to Render
3. Use the provided `render.yaml` configuration
4. Set environment variables in Render dashboard
5. Deploy with one click

### Other Platforms

- **Heroku**: Use `Procfile` and `runtime.txt`
- **Railway**: Auto-detects Python and uses `main.py`
- **PythonAnywhere**: Upload files and configure WSGI

## Bot Commands

### General Users
- `/start` - Initialize bot and show welcome
- `/help` - Display available commands and features
- `/chat <message>` - Chat with AI (or just send any message)
- `/translate <text>` - Translate text between languages
- `/wiki <query>` - Search Wikipedia
- `/crypto <symbol>` - Get cryptocurrency prices
- `/accessibility` - Toggle accessibility features
- `/speak <text>` - Text-to-speech conversion

### Entertainment  
- `/meme <description>` - Generate custom memes
- `/story <genre>` - Create personalized stories
- `/trivia` - Start trivia game
- `/wordgame` - Play word association games
- `/riddle` - Get challenging riddles
- `/workout <type>` - Generate fitness plans
- `/recipe <cuisine>` - Create custom recipes

### Admin Only (Hidden from regular users)
- `/admin` - Access comprehensive admin panel
- `/logs` - View user activity logs
- `/broadcast <message>` - Send messages to all users
- `/ban <user_id>` - Ban user from bot
- `/stats` - View detailed bot statistics

## Features Overview

### AI Personalities
- Professional, Casual, Creative, Technical, Educational, Empathetic
- Adaptive responses based on user interaction history
- Context-aware conversation management

### Group Management
- Automatic spam detection and content filtering
- Customizable moderation rules and banned words
- Complete member activity surveillance
- Per-group feature toggles

### Accessibility Support
- High-contrast text formatting for visual impairments
- Automatic text-to-speech for audio assistance
- Screen reader compatible responses
- User preference management

### Cryptocurrency Features
- Real-time price data from CoinGecko API
- AI-powered market predictions and analysis
- Portfolio tracking and management
- Price alerts and notifications

## File Structure

```
telegram-bot/
├── main.py                     # Entry point
├── bot_handlers.py            # Core bot logic
├── ai_services.py             # AI integrations
├── config.py                  # Configuration management
├── utils.py                   # Utility functions
├── services/
│   ├── accessibility_service.py
│   ├── advanced_ai_service.py
│   ├── animation_service.py
│   ├── content_generation_service.py
│   ├── games_service.py
│   ├── memory_service.py
│   └── [other services]
├── requirements.txt           # Python dependencies
├── render.yaml               # Render deployment config
├── Procfile                  # Process configuration
└── README.md                 # This file
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Create an issue for bug reports or feature requests
- Join our Telegram group: [Bot Support](https://t.me/your_support_group)
- Email: support@your-domain.com

## Changelog

- **June 2025**: Initial release with 50+ advanced features
- **Latest**: Streamlined interface focusing on core AI and entertainment features
- **Deployment**: Ready for production with 24/7 uptime support

---

**Note**: This bot includes comprehensive surveillance and logging capabilities for admin users. All user interactions are monitored and stored for analysis and improvement purposes.