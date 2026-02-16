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


    def get_accounts(self) -> Optional[List[Dict]]:
        """
        Retrieves list of available accounts.
        
        :param: None
        :return: List of account dictionaries or None if failed
        """
        
        accounts = self.api_client.get_accounts()  # Request accounts from API
        if accounts:  # Verify if accounts were retrieved
            self.accounts_cache = accounts  # Cache accounts list
        return accounts  # Return accounts list


    def get_account_id(self) -> Optional[str]:
        """
        Returns the account ID, selecting the first account if not set.
        
        :param: None
        :return: Account ID string or None if no accounts available
        """
        
        if self.account_id:  # Verify if account ID already set
            return self.account_id  # Return cached account ID
        
        accounts = self.get_accounts()  # Get accounts list
        if accounts and len(accounts) > 0:  # Verify if accounts exist
            self.account_id = accounts[0].get("id")  # Set account ID from first account
            return self.account_id  # Return account ID
        
        return None  # Return None if no accounts available


    def set_account_id(self, account_id: str) -> None:
        """
        Sets the account ID to use for operations.
        
        :param account_id: Account identifier
        :return: None
        """
        
        self.account_id = account_id  # Set account ID


    def get_balances(self) -> Optional[List[Dict]]:
        """
        Retrieves balances for the current account.
        
        :param: None
        :return: List of balance dictionaries or None if failed
        """
        
        account_id = self.get_account_id()  # Get account ID
        if not account_id:  # Verify if account ID is available
            return None  # Return None if no account ID
        
        return self.api_client.get_balances(account_id)  # Request balances from API


    def get_balance(self, symbol: str) -> Optional[Dict]:
        """
        Retrieves balance for a specific symbol.
        
        :param symbol: Currency symbol (e.g., BTC, BRL)
        :return: Balance dictionary or None if not found
        """
        
        balances = self.get_balances()  # Get all balances
        if not balances:  # Verify if balances retrieved
            return None  # Return None if no balances
        
        for balance in balances:  # Iterate through balances
            if balance.get("symbol") == symbol:  # Verify if symbol matches
                return balance  # Return matching balance
        
        return None  # Return None if symbol not found


    def get_available_balance(self, symbol: str) -> float:
        """
        Returns available balance for a specific symbol.
        
        :param symbol: Currency symbol (e.g., BTC, BRL)
        :return: Available balance as float, 0.0 if not found
        """
        
        balance = self.get_balance(symbol)  # Get balance for symbol
        if balance:  # Verify if balance exists
            available = balance.get("available", "0")  # Get available amount
            try:  # Attempt to convert to float
                return float(available)  # Return available balance as float
            except ValueError:  # Handle conversion error
                return 0.0  # Return 0.0 on error
        return 0.0  # Return 0.0 if balance not found


    def get_total_balance(self, symbol: str) -> float:
        """
        Returns total balance for a specific symbol.
        
        :param symbol: Currency symbol (e.g., BTC, BRL)
        :return: Total balance as float, 0.0 if not found
        """
        
        balance = self.get_balance(symbol)  # Get balance for symbol
        if balance:  # Verify if balance exists
            total = balance.get("total", "0")  # Get total amount
            try:  # Attempt to convert to float
                return float(total)  # Return total balance as float
            except ValueError:  # Handle conversion error
                return 0.0  # Return 0.0 on error
        return 0.0  # Return 0.0 if balance not found


    def get_all_orders(self) -> Optional[Dict]:
        """
        Retrieves all orders for the current account.
        
        :param: None
        :return: Dictionary containing all orders or None if failed
        """
        
        account_id = self.get_account_id()  # Get account ID
        if not account_id:  # Verify if account ID is available
            return None  # Return None if no account ID
        
        return self.api_client.get_all_orders(account_id)  # Request all orders from API


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
