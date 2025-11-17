"""Test configuration and fixtures."""

import pytest
import os

# Set test environment variables
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test_db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/1'
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'


@pytest.fixture
def mock_env():
    """Mock environment variables for testing."""
    return {
        'DATABASE_URL': os.environ['DATABASE_URL'],
        'REDIS_URL': os.environ['REDIS_URL'],
        'OPENAI_API_KEY': os.environ['OPENAI_API_KEY']
    }
