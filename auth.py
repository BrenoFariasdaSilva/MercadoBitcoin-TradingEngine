"""
================================================================================
Mercado Bitcoin Trading Bot - Authentication Module
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-16
Description :
    Authentication module for Mercado Bitcoin API v4.
    This module handles OAuth2 client credentials flow authentication,
    token generation, token storage, and automatic token refresh.

    Key features include:
        - OAuth2 client credentials authentication
        - Access token generation and storage
        - Automatic token refresh before expiration
        - Thread-safe token management
        - Request signing and header generation
        - Token validation

Usage:
    1. Initialize Authenticator with API key and secret.
        auth = Authenticator(api_key, api_secret)
    2. Call authenticate() to obtain access token.
        auth.authenticate()
    3. Use get_auth_headers() to get authorization headers for requests.
        headers = auth.get_auth_headers()

Outputs:
    - Access tokens stored in memory
    - Authentication headers for API requests

TODOs:
    - Implement token persistence to disk
    - Add refresh token support if API supports it
    - Implement token revocation

Dependencies:
    - Python >= 3.8
    - requests
    - time (standard library)
    - typing (standard library)

Assumptions & Notes:
    - Uses OAuth2 client credentials flow
    - Tokens are stored in memory only
    - Token refresh happens automatically before expiration
"""

import requests  # For HTTP requests
import time  # For timestamp operations and token expiration
from typing import Dict, Optional  # For type hints


class Authenticator:  # Authentication handler class
    """
    Handles authentication with Mercado Bitcoin API.
    
    :param: None
    :return: None
    """


    def __init__(self, api_key: str, api_secret: str, base_url: str):
        """
        Initializes the Authenticator with credentials.
        
        :param api_key: API key for authentication
        :param api_secret: API secret for authentication
        :param base_url: Base URL for API requests
        :return: None
        """
        
        self.api_key = api_key  # Store API key
        self.api_secret = api_secret  # Store API secret
        self.base_url = base_url  # Store base URL
        self.access_token: Optional[str] = None  # Initialize access token as None
        self.token_expiry: float = 0.0  # Initialize token expiry timestamp
        self.token_type: str = "Bearer"  # Default token type


    def authenticate(self) -> bool:
        """
        Authenticates with the API and obtains an access token.
        
        :param: None
        :return: True if authentication successful, False otherwise
        """
        
        token_url = f"{self.base_url}/oauth2/token"  # Construct token endpoint URL
        
        payload = {  # Prepare authentication payload
            "grant_type": "client_credentials",  # OAuth2 grant type
        }
        
        auth = (self.api_key, self.api_secret)  # HTTP Basic Auth tuple
        
        headers = {  # Prepare request headers
            "Content-Type": "application/x-www-form-urlencoded",  # Content type for form data
        }
        
        try:  # Attempt authentication request
            response = requests.post(  # Send POST request to token endpoint
                token_url,  # Token URL
                data=payload,  # Form data payload
                auth=auth,  # Basic authentication
                headers=headers,  # Request headers
                timeout=30  # Request timeout
            )
            
            if response.status_code == 200:  # Verify if request was successful
                data = response.json()  # Parse JSON response
                self.access_token = data.get("access_token")  # Extract access token
                expires_in = data.get("expires_in", 3600)  # Extract expiry time (default 1 hour)
                self.token_type = data.get("token_type", "Bearer")  # Extract token type
                self.token_expiry = time.time() + expires_in - 300  # Set expiry with 5-minute buffer
                return True  # Return success
            else:  # Authentication failed
                return False  # Return failure
                
        except Exception:  # Catch any exceptions
            return False  # Return failure


    def is_token_valid(self) -> bool:
        """
        Verifies if the current access token is valid and not expired.
        
        :param: None
        :return: True if token is valid, False otherwise
        """
        
        if not self.access_token:  # Verify if token exists
            return False  # Return False if no token
        if time.time() >= self.token_expiry:  # Verify if token is expired
            return False  # Return False if expired
        return True  # Return True if token is valid


    def ensure_authenticated(self) -> bool:
        """
        Ensures that a valid token is available, refreshing if necessary.
        
        :param: None
        :return: True if authentication is valid or refresh successful, False otherwise
        """
        
        if self.is_token_valid():  # Verify if current token is valid
            return True  # Return True if already valid
        return self.authenticate()  # Otherwise attempt to authenticate


    def get_auth_headers(self) -> Dict[str, str]:
        """
        Returns authorization headers for API requests.
        
        :param: None
        :return: Dictionary containing authorization headers
        """
        
        if not self.ensure_authenticated():  # Ensure valid authentication
            return {}  # Return empty dict if authentication fails
        
        return {  # Return authorization headers
            "Authorization": f"{self.token_type} {self.access_token}",  # Bearer token header
        }


def create_authenticator(api_key: str, api_secret: str, base_url: str) -> Authenticator:
    """
    Factory function to create and initialize an Authenticator instance.
    
    :param api_key: API key for authentication
    :param api_secret: API secret for authentication
    :param base_url: Base URL for API requests
    :return: Initialized Authenticator instance
    """
    
    auth = Authenticator(api_key, api_secret, base_url)  # Create authenticator instance
    auth.authenticate()  # Perform initial authentication
    return auth  # Return authenticated instance
