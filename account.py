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


    def get_orders_for_symbol(self, symbol: str) -> Optional[List[Dict]]:
        """
        Retrieves orders for a specific symbol.
        
        :param symbol: Trading pair symbol (e.g., BTC-BRL)
        :return: List of order dictionaries or None if failed
        """
        
        account_id = self.get_account_id()  # Get account ID
        if not account_id:  # Verify if account ID is available
            return None  # Return None if no account ID
        
        return self.api_client.get_orders(account_id, symbol)  # Request orders from API


    def calculate_average_price(self, crypto_symbol: str, trading_pair: str) -> Optional[float]:
        """
        Calculates average purchase price for a cryptocurrency from executions.
        
        :param crypto_symbol: Cryptocurrency symbol (e.g., BTC)
        :param trading_pair: Trading pair symbol (e.g., BTC-BRL)
        :return: Average price as float or None if no executions
        """
        
        all_orders_data = self.get_all_orders()  # Get all orders
        if not all_orders_data:  # Verify if orders data exists
            return None  # Return None if no orders data
        
        orders = all_orders_data.get("items", [])  # Extract orders list from response
        
        total_cost = 0.0  # Initialize total cost accumulator
        total_qty = 0.0  # Initialize total quantity accumulator
        
        for order in orders:  # Iterate through all orders
            if order.get("instrument") != trading_pair:  # Verify if order is for the trading pair
                continue  # Skip orders for other pairs
            
            if order.get("side") != "buy":  # Verify if order is a buy order
                continue  # Skip sell orders
            
            executions = order.get("executions", [])  # Get executions list
            
            for execution in executions:  # Iterate through executions
                price = execution.get("price")  # Get execution price
                qty = execution.get("qty")  # Get execution quantity
                
                if price is None or qty is None:  # Verify if price and quantity exist
                    continue  # Skip incomplete executions
                
                try:  # Attempt to convert and calculate
                    exec_price = float(price)  # Convert price to float
                    exec_qty = float(qty)  # Convert quantity to float
                    total_cost += exec_price * exec_qty  # Add to total cost
                    total_qty += exec_qty  # Add to total quantity
                except (ValueError, TypeError):  # Handle conversion errors
                    continue  # Skip invalid executions
        
        if total_qty > 0:  # Verify if any quantity was accumulated
            return total_cost / total_qty  # Return weighted average price
        
        return None  # Return None if no buy executions found


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
