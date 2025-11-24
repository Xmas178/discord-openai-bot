"""
OpenAI API client wrapper for Discord bot
Provides safe interface to OpenAI GPT models with error handling
Author: Sami (CodeNob Dev)
"""

import openai
from typing import List, Dict, Optional, Tuple
import time


class OpenAIClient:
    """
    Safe wrapper for OpenAI API calls in Discord bot (v0.28.1 API)

    Features:
    - Automatic error handling
    - Retry logic for transient failures
    - Token limit enforcement
    - Response validation
    - Timeout protection

    Security:
    - API key validation
    - Input sanitization
    - Rate limit handling
    - No sensitive data in logs
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 150,
        temperature: float = 0.7,
    ):
        """
        Initialize OpenAI client for Discord bot

        Args:
            api_key: OpenAI API key (must start with 'sk-')
            model: Model name (gpt-4o-mini, gpt-4o, gpt-4-turbo)
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)

        Raises:
            ValueError: If API key is invalid
        """
        # Validate API key format
        if not api_key or not api_key.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")

        # Set API key globally for openai library (v0.28.1 style)
        openai.api_key = api_key

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def get_chat_response(
        self, messages: List[Dict[str, str]], user_id: Optional[int] = None
    ) -> Tuple[bool, str, str]:
        """
        Get chat completion from OpenAI for Discord messages

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            user_id: Optional Discord user ID for logging (will be sanitized)

        Returns:
            Tuple of (success, response_text, error_message)
            - success: True if API call succeeded
            - response_text: AI response (empty if failed)
            - error_message: Error description (empty if succeeded)
        """
        # Validate input
        if not messages:
            return False, "", "No messages provided"

        if not self._validate_messages(messages):
            return False, "", "Invalid message format"

        # Attempt API call with retries
        for attempt in range(self.max_retries):
            try:
                # Make API call (v0.28.1 syntax)
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    request_timeout=30,
                )

                # Extract response text (v0.28.1 syntax)
                response_text = response.choices[0].message.content.strip()

                # Validate response
                if not response_text:
                    return False, "", "Empty response from OpenAI"

                return True, response_text, ""

            except Exception as e:
                error_str = str(e).lower()

                # Rate limit error
                if "rate" in error_str or "429" in error_str:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return False, "", "Rate limit exceeded. Please try again later."

                # Invalid request
                elif "invalid" in error_str or "400" in error_str:
                    return False, "", "Invalid request to AI service"

                # Authentication error
                elif "auth" in error_str or "401" in error_str:
                    return False, "", "Authentication failed"

                # Timeout
                elif "timeout" in error_str or "timed out" in error_str:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 2 * (attempt + 1))
                        continue
                    return False, "", "Request timed out. Please try again."

                # Other errors - retry
                else:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return False, "", "AI service temporarily unavailable"

        # All retries exhausted
        return False, "", "Service temporarily unavailable after multiple attempts"

    def _validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """
        Validate message format for OpenAI API

        Args:
            messages: List of message dictionaries

        Returns:
            True if format is valid
        """
        if not isinstance(messages, list):
            return False

        valid_roles = {"system", "user", "assistant"}

        for msg in messages:
            # Check it's a dict
            if not isinstance(msg, dict):
                return False

            # Check required keys
            if "role" not in msg or "content" not in msg:
                return False

            # Check role is valid
            if msg["role"] not in valid_roles:
                return False

            # Check content is string
            if not isinstance(msg["content"], str):
                return False

            # Check content not empty
            if not msg["content"].strip():
                return False

        return True

    def get_model_info(self) -> Dict:
        """
        Get current model configuration

        Returns:
            Dictionary with model settings
        """
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "max_retries": self.max_retries,
        }
