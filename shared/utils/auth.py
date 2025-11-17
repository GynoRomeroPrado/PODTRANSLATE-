"""Authentication and user management utilities."""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
import os


class AuthService:
    """Service for authentication and JWT token management."""

    def __init__(self):
        """Initialize auth service."""
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-this')
        self.jwt_algorithm = 'HS256'
        self.jwt_expiration_days = int(os.getenv('JWT_EXPIRES_IN_DAYS', 7))

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )

    def create_access_token(self, user_id: str, email: str) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            JWT token
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=self.jwt_expiration_days),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token

    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def create_api_key(self) -> tuple[str, str]:
        """
        Create an API key.

        Returns:
            Tuple of (api_key, api_key_hash)
        """
        import secrets

        # Generate random API key
        api_key = f"pt_{secrets.token_urlsafe(32)}"

        # Hash it for storage
        api_key_hash = self.hash_password(api_key)

        return api_key, api_key_hash

    def verify_api_key(self, api_key: str, api_key_hash: str) -> bool:
        """
        Verify an API key.

        Args:
            api_key: API key to verify
            api_key_hash: Stored hash

        Returns:
            True if valid
        """
        return self.verify_password(api_key, api_key_hash)
