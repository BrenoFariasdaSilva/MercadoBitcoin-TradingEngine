"""
================================================================================
Mercado Bitcoin Trading Bot - Account Management Module
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-16
Description :
    Account management module for Mercado Bitcoin trading bot.
    This module handles account-related operations including balance retrieval,
    average price calculation from executed trades, and position management.

    Key features include:
        - Account selection and management
        - Balance retrieval and tracking
        - Average price calculation from order executions
        - Position monitoring
        - Available balance calculation
        - Account state caching

Usage:
    1. Initialize AccountManager with an APIClient instance.
        account_mgr = AccountManager(api_client)
    2. Select or get the default account.
        account_id = account_mgr.get_account_id()
    3. Retrieve balances and calculate averages.
        balances = account_mgr.get_balances()
        avg_price = account_mgr.get_average_price("BTC")

Outputs:
    - Account balances
    - Average purchase prices
    - Position information

TODOs:
    - Implement balance change detection
    - Add support for multiple account management
    - Cache average price calculations

Dependencies:
    - Python >= 3.8
    - typing (standard library)

Assumptions & Notes:
    - Uses first available account by default
    - Average price is calculated from all executed orders
    - Balances are retrieved fresh on each call
"""

from typing import Dict, List, Optional  # For type hints


class AccountManager:
    """
    Manages account operations and data.
    
    :param: None
    :return: None
    """


    def __init__(self, api_client):
        """
        Initializes the AccountManager.
        
        :param api_client: APIClient instance for API operations
        :return: None
        """
        
        self.api_client = api_client  # Store API client instance
        self.account_id: Optional[str] = None  # Initialize account ID as None
        self.accounts_cache: Optional[List[Dict]] = None  # Cache for accounts list


    def get_positions(self) -> Optional[List[Dict]]:
        """
        Retrieves positions for the current account.
        
        :param: None
        :return: List of position dictionaries or None if failed
        """
        
        account_id = self.get_account_id()  # Get account ID
        if not account_id:  # Verify if account ID is available
            return None  # Return None if no account ID
        
        return self.api_client.get_positions(account_id)  # Request positions from API


def create_account_manager(api_client) -> AccountManager:
    """
    Factory function to create an AccountManager instance.
    
    :param api_client: APIClient instance for API operations
    :return: Initialized AccountManager instance
    """
    
    return AccountManager(api_client)  # Create and return AccountManager instance
