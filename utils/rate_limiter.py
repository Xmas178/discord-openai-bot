"""
Rate limiting utility for Discord bot
Prevents spam and API abuse by limiting requests per user
Author: Sami (CodeNob Dev)
"""

import time
from collections import defaultdict, deque
from typing import Dict, Deque


class RateLimiter:
    """
    Simple in-memory rate limiter to prevent spam in Discord bot

    Tracks requests per user and enforces a maximum rate.
    Uses a sliding window approach with timestamps.

    Security features:
    - Per-user rate limiting
    - Configurable time window
    - Automatic cleanup of old entries
    - Thread-safe for single-process bots
    """

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter for Discord bot

        Args:
            max_requests: Maximum requests allowed per time window
            time_window: Time window in seconds (default: 60 = 1 minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window

        # Store timestamps of requests per user
        # Key: user_id, Value: deque of timestamps
        self.user_requests: Dict[int, Deque[float]] = defaultdict(deque)

        # Track when we last cleaned up old entries
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # Cleanup every 5 minutes

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if Discord user is allowed to make a request

        Args:
            user_id: Discord user ID

        Returns:
            True if user can make request, False if rate limited
        """
        current_time = time.time()

        # Perform periodic cleanup
        self._cleanup_if_needed(current_time)

        # Get user's request history
        user_queue = self.user_requests[user_id]

        # Remove requests outside the time window
        cutoff_time = current_time - self.time_window
        while user_queue and user_queue[0] < cutoff_time:
            user_queue.popleft()

        # Check if user has exceeded rate limit
        current_count = len(user_queue)

        if current_count < self.max_requests:
            # User is allowed, record this request
            user_queue.append(current_time)
            return True
        else:
            # User has exceeded rate limit
            return False

    def get_wait_time(self, user_id: int) -> int:
        """
        Get how long Discord user must wait before next request is allowed

        Args:
            user_id: Discord user ID

        Returns:
            Seconds until next request is allowed (0 if allowed now)
        """
        user_queue = self.user_requests[user_id]

        if not user_queue or len(user_queue) < self.max_requests:
            return 0

        # Calculate when the oldest request will expire
        oldest_request = user_queue[0]
        current_time = time.time()
        wait_time = int(self.time_window - (current_time - oldest_request))

        return max(0, wait_time)

    def reset_user(self, user_id: int):
        """
        Reset rate limit for a specific Discord user

        Args:
            user_id: Discord user ID to reset
        """
        if user_id in self.user_requests:
            del self.user_requests[user_id]

    def _cleanup_if_needed(self, current_time: float):
        """
        Clean up old user entries to prevent memory bloat

        Args:
            current_time: Current timestamp
        """
        # Only cleanup every cleanup_interval seconds
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        # Remove users with no recent requests
        cutoff_time = current_time - self.time_window
        users_to_remove = []

        for user_id, queue in self.user_requests.items():
            # Remove old timestamps from queue
            while queue and queue[0] < cutoff_time:
                queue.popleft()

            # If queue is empty, mark user for removal
            if not queue:
                users_to_remove.append(user_id)

        # Remove inactive users
        for user_id in users_to_remove:
            del self.user_requests[user_id]

        self.last_cleanup = current_time

    def get_stats(self) -> Dict:
        """
        Get current rate limiter statistics

        Returns:
            Dictionary with statistics about current state
        """
        return {
            "active_users": len(self.user_requests),
            "max_requests": self.max_requests,
            "time_window_seconds": self.time_window,
            "last_cleanup": self.last_cleanup,
        }
