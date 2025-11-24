"""
Discord OpenAI Bot
Main bot module with message handling and commands
Author: Sami (CodeNob Dev)
"""

import discord
from discord.ext import commands
from typing import Dict, List

from config import config
from utils.openai_client import OpenAIClient
from utils.rate_limiter import RateLimiter
from utils.validators import InputValidator

# Create bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize utilities
openai_client = OpenAIClient(
    api_key=config.openai_api_key,
    model=config.openai_model,
    max_tokens=config.openai_max_tokens,
    temperature=config.openai_temperature,
)
rate_limiter = RateLimiter()
validator = InputValidator()

# Store conversation context per user
user_contexts: Dict[int, List[Dict[str, str]]] = {}


@bot.event
async def on_ready() -> None:
    """Called when bot is ready and connected to Discord"""
    print(f"{bot.user} has connected to Discord!")
    print(f"Bot is in {len(bot.guilds)} servers")


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Handle incoming messages

    Args:
        message: Discord message object
    """
    # Ignore own messages
    if message.author == bot.user:
        return

    # Process commands first
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    # Check rate limit
    if not rate_limiter.is_allowed(message.author.id):
        wait_time = rate_limiter.get_wait_time(message.author.id)
        await message.channel.send(
            f"Please wait {wait_time} seconds before sending another message."
        )
        return

    # Validate message
    is_valid, cleaned_text, error = validator.validate_message(message.content)
    if not is_valid:
        await message.channel.send(f"Error: {error}")
        return

    # Get or create user context
    user_id = message.author.id
    if user_id not in user_contexts:
        user_contexts[user_id] = []

    # Add user message to context
    user_contexts[user_id].append({"role": "user", "content": cleaned_text})

    # Keep only last N messages
    max_messages = config.max_context_length * 2
    if len(user_contexts[user_id]) > max_messages:
        user_contexts[user_id] = user_contexts[user_id][-max_messages:]

    # Show typing indicator
    async with message.channel.typing():
        # Get AI response (synchronous call, returns tuple)
        success, response_text, error_message = openai_client.get_chat_response(
            user_contexts[user_id]
        )

        # Check if request succeeded
        if not success:
            await message.channel.send(f"Error: {error_message}")
            return

    # Add AI response to context
    user_contexts[user_id].append({"role": "assistant", "content": response_text})

    # Send response
    await message.channel.send(response_text)


@bot.command(name="ping")
async def ping(ctx: commands.Context) -> None:
    """
    Test command to check if bot is responding

    Args:
        ctx: Command context
    """
    await ctx.send("Pong!")


@bot.command(name="clear")
async def clear_context(ctx: commands.Context) -> None:
    """
    Clear user's conversation context

    Args:
        ctx: Command context
    """
    user_id = ctx.author.id
    if user_id in user_contexts:
        user_contexts[user_id] = []
    await ctx.send("Conversation context cleared!")


if __name__ == "__main__":
    bot.run(config.discord_token)
"""
Discord OpenAI Bot
Main bot module with message handling and commands
Author: Sami (CodeNob Dev)
"""

import discord
from discord.ext import commands
from typing import Dict, List

from config import config
from utils.openai_client import OpenAIClient
from utils.rate_limiter import RateLimiter
from utils.validators import Validator

# Create bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize utilities
openai_client = OpenAIClient()
rate_limiter = RateLimiter()
validator = Validator()

# Store conversation context per user
user_contexts: Dict[int, List[Dict[str, str]]] = {}


@bot.event
async def on_ready() -> None:
    """Called when bot is ready and connected to Discord"""
    print(f"{bot.user} has connected to Discord!")
    print(f"Bot is in {len(bot.guilds)} servers")


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Handle incoming messages

    Args:
        message: Discord message object
    """
    # Ignore own messages
    if message.author == bot.user:
        return

    # Ignore if message starts with command prefix
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    # Check rate limit
    if not rate_limiter.is_allowed(message.author.id):
        wait_time = rate_limiter.get_wait_time(message.author.id)
        await message.channel.send(
            f"Please wait {wait_time} seconds before sending another message."
        )
        return

    # Validate message
    is_valid, error = validator.validate_message(message.content)
    if not is_valid:
        await message.channel.send(f"Error: {error}")
        return

    # Get or create user context
    user_id = message.author.id
    if user_id not in user_contexts:
        user_contexts[user_id] = []

    # Add user message to context
    user_contexts[user_id].append({"role": "user", "content": message.content})

    # Keep only last N messages
    max_messages = config.max_context_length * 2
    if len(user_contexts[user_id]) > max_messages:
        user_contexts[user_id] = user_contexts[user_id][-max_messages:]

    # Show typing indicator
    async with message.channel.typing():
        # Get AI response
        response = await openai_client.get_response(user_contexts[user_id])

    # Add AI response to context
    user_contexts[user_id].append({"role": "assistant", "content": response})

    # Send response
    await message.channel.send(response)


@bot.command(name="ping")
async def ping(ctx: commands.Context) -> None:
    """
    Test command to check if bot is responding

    Args:
        ctx: Command context
    """
    await ctx.send("Pong!")


@bot.command(name="clear")
async def clear_context(ctx: commands.Context) -> None:
    """
    Clear user's conversation context

    Args:
        ctx: Command context
    """
    user_id = ctx.author.id
    if user_id in user_contexts:
        user_contexts[user_id] = []
    await ctx.send("Conversation context cleared!")


@bot.command(name="help")
async def help_command(ctx: commands.Context) -> None:
    """
    Show help message with available commands

    Args:
        ctx: Command context
    """
    help_text = """
**Discord Bot Commands:**

Chat: Send a message to talk with AI
!ping - Test bot response
!clear - Clear conversation history
!help - Show this help message

Rate limit: One message every 3 seconds
    """
    await ctx.send(help_text)


if __name__ == "__main__":
    bot.run(config.discord_token)
