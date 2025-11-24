"""
Configuration module for Discord Bot
Validates and provides access to environment variables
Author: Sami (CodeNob Dev)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BotConfig:
    """
    Configuration class that loads and validates environment variables
    """

    def __init__(self):
        """Initialize configuration from environment variables"""
        # Discord configuration
        self.discord_token = os.getenv("DISCORD_TOKEN")
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN environment variable is required")

        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "150"))
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

        # Rate limiting configuration
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "20"))
        self.rate_limit_seconds = int(os.getenv("RATE_LIMIT_SECONDS", "3"))

        # Message configuration
        self.max_context_length = int(os.getenv("MAX_CONTEXT_LENGTH", "10"))
        self.max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))

        # Database configuration
        self.db_path = os.getenv("DB_PATH", "discord_bot.db")


# Create global config instance
config = BotConfig()
