"""Advanced rate limiting with Redis."""

import redis
import time
import hashlib
from typing import Optional, Tuple
from functools import wraps
from fastapi import HTTPException, Request


class RateLimiter:
    """
    Redis-backed rate limiter with multiple strategies.

    Supports:
    - Fixed window
    - Sliding window
    - Token bucket
    """

    def __init__(self, redis_url: str):
        """Initialize rate limiter with Redis connection."""
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

    def _get_identifier(self, request: Request, identifier: Optional[str] = None) -> str:
        """
        Get unique identifier for rate limiting.

        Args:
            request: FastAPI request
            identifier: Optional custom identifier

        Returns:
            Unique identifier string
        """
        if identifier:
            return identifier

        # Use API key if present
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()}"

        # Use user ID if authenticated
        # user_id = getattr(request.state, 'user_id', None)
        # if user_id:
        #     return f"user:{user_id}"

        # Fallback to IP address
        client_ip = request.client.host
        return f"ip:{client_ip}"

    def fixed_window(
        self,
        max_requests: int,
        window_seconds: int,
        identifier: Optional[str] = None
    ):
        """
        Fixed window rate limiter decorator.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Window size in seconds
            identifier: Optional custom identifier

        Example:
            @rate_limiter.fixed_window(max_requests=100, window_seconds=60)
            async def my_endpoint():
                pass
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                key = self._get_identifier(request, identifier)

                # Create window key
                current_window = int(time.time()) // window_seconds
                window_key = f"rate_limit:fixed:{key}:{current_window}"

                # Increment counter
                current_count = self.redis_client.incr(window_key)

                # Set expiry on first request
                if current_count == 1:
                    self.redis_client.expire(window_key, window_seconds)

                # Check limit
                if current_count > max_requests:
                    # Calculate reset time
                    reset_time = (current_window + 1) * window_seconds

                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Rate limit exceeded",
                            "limit": max_requests,
                            "window": window_seconds,
                            "reset_at": reset_time
                        }
                    )

                # Add rate limit headers
                # response.headers['X-RateLimit-Limit'] = str(max_requests)
                # response.headers['X-RateLimit-Remaining'] = str(max_requests - current_count)

                return await func(request, *args, **kwargs)

            return wrapper
        return decorator

    def sliding_window(
        self,
        max_requests: int,
        window_seconds: int,
        identifier: Optional[str] = None
    ):
        """
        Sliding window rate limiter decorator.

        More accurate than fixed window, prevents burst at window boundaries.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Window size in seconds
            identifier: Optional custom identifier
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                key = self._get_identifier(request, identifier)
                window_key = f"rate_limit:sliding:{key}"

                current_time = time.time()
                window_start = current_time - window_seconds

                # Remove old entries
                self.redis_client.zremrangebyscore(window_key, 0, window_start)

                # Count requests in window
                request_count = self.redis_client.zcard(window_key)

                if request_count >= max_requests:
                    # Get oldest request time for reset calculation
                    oldest = self.redis_client.zrange(window_key, 0, 0, withscores=True)
                    reset_time = oldest[0][1] + window_seconds if oldest else current_time

                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Rate limit exceeded",
                            "limit": max_requests,
                            "window": window_seconds,
                            "reset_at": int(reset_time)
                        }
                    )

                # Add current request
                self.redis_client.zadd(window_key, {str(current_time): current_time})

                # Set expiry
                self.redis_client.expire(window_key, window_seconds)

                return await func(request, *args, **kwargs)

            return wrapper
        return decorator

    def token_bucket(
        self,
        capacity: int,
        refill_rate: float,
        identifier: Optional[str] = None
    ):
        """
        Token bucket rate limiter decorator.

        Allows bursts while maintaining average rate.

        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
            identifier: Optional custom identifier
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                key = self._get_identifier(request, identifier)
                bucket_key = f"rate_limit:bucket:{key}"

                current_time = time.time()

                # Get or initialize bucket
                pipe = self.redis_client.pipeline()
                pipe.hget(bucket_key, 'tokens')
                pipe.hget(bucket_key, 'last_refill')
                tokens, last_refill = pipe.execute()

                tokens = float(tokens) if tokens else capacity
                last_refill = float(last_refill) if last_refill else current_time

                # Refill tokens
                time_passed = current_time - last_refill
                tokens_to_add = time_passed * refill_rate
                tokens = min(capacity, tokens + tokens_to_add)

                # Check if we have tokens
                if tokens < 1:
                    wait_time = (1 - tokens) / refill_rate

                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Rate limit exceeded",
                            "capacity": capacity,
                            "refill_rate": refill_rate,
                            "retry_after": int(wait_time)
                        }
                    )

                # Consume token
                tokens -= 1

                # Update bucket
                pipe = self.redis_client.pipeline()
                pipe.hset(bucket_key, 'tokens', tokens)
                pipe.hset(bucket_key, 'last_refill', current_time)
                pipe.expire(bucket_key, int(capacity / refill_rate) + 60)
                pipe.execute()

                return await func(request, *args, **kwargs)

            return wrapper
        return decorator

    def get_limits(self, request: Request) -> dict:
        """
        Get current rate limit status for a request.

        Args:
            request: FastAPI request

        Returns:
            Dictionary with rate limit information
        """
        key = self._get_identifier(request)

        # Check different limit types
        limits = {}

        # Fixed window
        current_window = int(time.time()) // 60
        fixed_key = f"rate_limit:fixed:{key}:{current_window}"
        fixed_count = self.redis_client.get(fixed_key)
        limits['fixed_window'] = int(fixed_count) if fixed_count else 0

        # Sliding window
        sliding_key = f"rate_limit:sliding:{key}"
        sliding_count = self.redis_client.zcard(sliding_key)
        limits['sliding_window'] = sliding_count

        # Token bucket
        bucket_key = f"rate_limit:bucket:{key}"
        tokens = self.redis_client.hget(bucket_key, 'tokens')
        limits['tokens_available'] = float(tokens) if tokens else None

        return limits
