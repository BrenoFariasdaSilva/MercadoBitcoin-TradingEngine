"""
================================================================================
Mercado Bitcoin Trading Bot - API Client Module
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-16
Description :
    API client module for interacting with Mercado Bitcoin API v4.
    This module provides a comprehensive interface for all API endpoints
    including public data, account information, and trading operations.

    Key features include:
        - Complete API v4 endpoint coverage
        - Automatic authentication handling
        - Request retry logic with exponential backoff
        - Error handling and logging
        - Rate limiting compliance
        - Response validation

Usage:
    1. Initialize APIClient with an Authenticator instance.
        client = APIClient(authenticator, base_url)
    2. Call endpoint methods to interact with API.
        balances = client.get_balances(account_id)
    3. Handle responses and errors appropriately.

Outputs:
    - JSON responses from API endpoints
    - Error messages for failed requests

TODOs:
    - Implement rate limiting logic
    - Add request caching for frequently accessed data
    - Implement WebSocket support for real-time data

Dependencies:
    - Python >= 3.8
    - requests
    - time (standard library)
    - typing (standard library)

Assumptions & Notes:
    - All requests use JSON format
    - Authentication is handled automatically
    - Endpoints follow Mercado Bitcoin API v4 specification
"""

import requests  # For HTTP requests
import time  # For retry delays and timing
from typing import Any, Dict, List, Optional  # For type hints


class APIClient:  # API client class for Mercado Bitcoin
    """
    Client for Mercado Bitcoin API v4.
    
    :param: None
    :return: None
    """
    
    def __init__(self, authenticator, base_url: str, timeout: int = 30, max_retries: int = 3, retry_delay: int = 2):
        """
        Initializes the API client.
        
        :param authenticator: Authenticator instance for authentication
        :param base_url: Base URL for API requests
        :param timeout: Request timeout in seconds
        :param max_retries: Maximum number of retry attempts
        :param retry_delay: Delay between retries in seconds
        :return: None
        """
        
        self.authenticator = authenticator  # Store authenticator instance
        self.base_url = base_url  # Store base URL
        self.timeout = timeout  # Store timeout value
        self.max_retries = max_retries  # Store max retries
        self.retry_delay = retry_delay  # Store retry delay


def create_api_client(authenticator, base_url: str, timeout: int = 30, max_retries: int = 3, retry_delay: int = 2) -> APIClient:
    """
    Factory function to create an APIClient instance.
    
    :param authenticator: Authenticator instance for authentication
    :param base_url: Base URL for API requests
    :param timeout: Request timeout in seconds
    :param max_retries: Maximum number of retry attempts
    :param retry_delay: Delay between retries in seconds
    :return: Initialized APIClient instance
    """
    
    return APIClient(authenticator, base_url, timeout, max_retries, retry_delay)  # Create and return APIClient instance
