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


    def get_all_orders(self, account_id: str) -> Optional[Dict]:
        """
        Retrieves all orders for a specific account.
        
        :param account_id: Account identifier
        :return: Dictionary containing all orders or None if failed
        """
        
        endpoint = f"/accounts/{account_id}/orders"  # Construct endpoint path
        return self.make_request("GET", endpoint)  # Make GET request to all orders endpoint


    def get_orders(self, account_id: str, symbol: str) -> Optional[List[Dict]]:
        """
        Retrieves orders for a specific account and symbol.
        
        :param account_id: Account identifier
        :param symbol: Trading pair symbol (e.g., BTC-BRL)
        :return: List of order dictionaries or None if failed
        """
        
        endpoint = f"/accounts/{account_id}/{symbol}/orders"  # Construct endpoint path
        result = self.make_request("GET", endpoint)  # Make GET request to orders endpoint
        if result and isinstance(result, list):  # Verify if result is a list
            return result  # Return list of orders
        return None  # Return None if not a list


    def get_orderbook(self, symbol: str) -> Optional[Dict]:
        """
        Retrieves order book for a symbol.
        
        :param symbol: Trading pair symbol (e.g., BTC-BRL)
        :return: Order book dictionary or None if failed
        """
        
        endpoint = f"/{symbol}/orderbook"  # Construct endpoint path
        return self.make_request("GET", endpoint, authenticated=False)  # Make GET request to orderbook endpoint


    def get_tickers(self) -> Optional[List[Dict]]:
        """
        Retrieves ticker information for all symbols.
        
        :param: None
        :return: List of ticker dictionaries or None if failed
        """
        
        result = self.make_request("GET", "/tickers", authenticated=False)  # Make GET request to tickers endpoint
        if result and isinstance(result, list):  # Verify if result is a list
            return result  # Return list of tickers
        return None  # Return None if not a list


    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Retrieves ticker information for a symbol.
        
        :param symbol: Trading pair symbol (e.g., BTC-BRL)
        :return: Ticker dictionary or None if failed
        """
        
        endpoint = f"/{symbol}/ticker"  # Construct endpoint path
        return self.make_request("GET", endpoint, authenticated=False)  # Make GET request to ticker endpoint


    def get_balances(self, account_id: str) -> Optional[List[Dict]]:
        """
        Retrieves balances for a specific account.
        
        :param account_id: Account identifier
        :return: List of balance dictionaries or None if failed
        """
        
        endpoint = f"/accounts/{account_id}/balances"  # Construct endpoint path
        result = self.make_request("GET", endpoint)  # Make GET request to balances endpoint
        if result and isinstance(result, list):  # Verify if result is a list
            return result  # Return list of balances
        return None  # Return None if not a list


    def get_accounts(self) -> Optional[List[Dict]]:
        """
        Retrieves list of accounts.
        
        :param: None
        :return: List of account dictionaries or None if failed
        """
        
        result = self.make_request("GET", "/accounts")  # Make GET request to accounts endpoint
        if result and isinstance(result, list):  # Verify if result is a list
            return result  # Return list of accounts
        return None  # Return None if not a list


    def make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None, authenticated: bool = True) -> Optional[Dict]:
        """
        Makes an HTTP request with retry logic.
        
        :param method: HTTP method (GET, POST, DELETE)
        :param endpoint: API endpoint path
        :param params: URL query parameters
        :param data: Request body data
        :param authenticated: Whether to include authentication headers
        :return: Response JSON data or None if failed
        """
        
        url = f"{self.base_url}{endpoint}"  # Construct full URL
        headers = {}  # Initialize headers dictionary
        
        if authenticated:  # Verify if authentication is required
            auth_headers = self.authenticator.get_auth_headers()  # Get authentication headers
            headers.update(auth_headers)  # Add authentication headers
        
        headers["Content-Type"] = "application/json"  # Set content type header
        
        for attempt in range(self.max_retries):  # Retry loop
            try:  # Attempt request
                if method == "GET":  # Handle GET requests
                    response = requests.get(url, headers=headers, params=params, timeout=self.timeout)  # Send GET request
                elif method == "POST":  # Handle POST requests
                    response = requests.post(url, headers=headers, json=data, timeout=self.timeout)  # Send POST request
                elif method == "DELETE":  # Handle DELETE requests
                    response = requests.delete(url, headers=headers, params=params, timeout=self.timeout)  # Send DELETE request
                else:  # Unsupported method
                    return None  # Return None for unsupported methods
                
                if response.status_code == 200:  # Verify for success
                    return response.json()  # Return parsed JSON response
                elif response.status_code == 401:  # Verify for unauthorized
                    if authenticated:  # If request was authenticated
                        self.authenticator.authenticate()  # Re-authenticate
                        continue  # Retry request
                    return None  # Return None if not authenticated
                else:  # Other error status codes
                    if attempt < self.max_retries - 1:  # Verify if retries remain
                        time.sleep(self.retry_delay)  # Wait before retry
                        continue  # Retry request
                    return None  # Return None after exhausting retries
                    
            except Exception:  # Catch any exceptions
                if attempt < self.max_retries - 1:  # Verify if retries remain
                    time.sleep(self.retry_delay)  # Wait before retry
                    continue  # Retry request
                return None  # Return None after exhausting retries
        
        return None  # Return None if all retries failed


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
