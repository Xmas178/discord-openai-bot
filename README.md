# Discord OpenAI Bot

AI-powered Discord bot with OpenAI GPT-4o-mini integration. Features conversation context, rate limiting, and input validation.

## Features

- OpenAI GPT-4o-mini integration for intelligent conversations
- Per-user conversation context (remembers last 10 messages)
- Rate limiting (max 10 requests/minute, 3 seconds between messages)
- Input validation and sanitization
- Slash commands (!ping, !clear)
- Error handling and retry logic
- 24/7 deployment ready

## Tech Stack

- Python 3.12
- discord.py 2.4+
- OpenAI API (GPT-4o-mini)
- Railway.app (deployment)

## Installation

### Prerequisites

- Python 3.12+
- Discord Bot Token
- OpenAI API Key

### Setup

1. Clone repository:
```bash
git clone https://github.com/Xmas178/discord-openai-bot.git
cd discord-openai-bot
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=150
OPENAI_TEMPERATURE=0.7
MAX_CONTEXT_LENGTH=10
RATE_LIMIT_SECONDS=3
MAX_MESSAGE_LENGTH=2000
```

5. Run bot:
```bash
python3 bot.py
```

## Usage

### Chat with Bot

Simply send a message in any channel where the bot has permissions. The bot will respond using OpenAI and remember your conversation context.

### Commands

- `!ping` - Test if bot is responding
- `!clear` - Clear your conversation history

### Rate Limits

- Maximum 10 messages per minute per user
- Minimum 3 seconds between messages

## Project Structure
```
discord-openai-bot/
├── bot.py              # Main bot logic
├── config.py           # Configuration management
├── utils/              # Utility modules
│   ├── openai_client.py    # OpenAI API wrapper
│   ├── rate_limiter.py     # Rate limiting
│   └── validators.py       # Input validation
├── .env                # Environment variables (not in git)
├── .gitignore
├── requirements.txt
└── README.md
```

## Security Features

- API key validation
- Input sanitization (XSS, SQL injection prevention)
- Rate limiting per user
- Maximum message length enforcement
- Dangerous pattern detection
- No sensitive data in logs

## Deployment

### Railway.app

1. Push code to GitHub
2. Connect Railway to your repository
3. Add environment variables in Railway dashboard
4. Deploy automatically

### Environment Variables (Railway)
```
DISCORD_TOKEN=your_token
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
```

## Development

### Running Tests
```bash
# Test individual modules
python3 -m utils.validators
python3 -m utils.rate_limiter
```

### Code Style

- English comments and docstrings
- Type hints for all functions
- Comprehensive error handling
- Security-first approach

## Author

**Sami** (CodeNob Dev)
- Portfolio: [tommilammi.fi](https://tommilammi.fi)
- GitHub: [@Xmas178](https://github.com/Xmas178)

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with discord.py
- Powered by OpenAI GPT-4o-mini
- Deployed on Railway.app