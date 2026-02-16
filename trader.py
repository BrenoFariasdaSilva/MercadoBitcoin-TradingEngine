"""
================================================================================
Mercado Bitcoin Trading Bot - Trading Logic Module
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-16
Description :
    Trading logic module implementing rule-based automated trading strategies.
    This module monitors cryptocurrency prices, evaluates trading rules,
    and executes buy/sell orders based on predefined thresholds.

    Key features include:
        - Real-time price monitoring
        - Rule-based trading decision engine
        - Automatic order execution
        - Duplicate execution prevention
        - Percentage-based position sizing
        - Average price tracking and comparison
        - Safety verifies for balance and API failures

Usage:
    1. Initialize TradingBot with required dependencies.
        bot = TradingBot(api_client, account_manager, config)
    2. Start monitoring and trading.
        bot.run()
    3. Bot will continuously monitor and execute trades based on rules.

Outputs:
    - Market buy/sell orders
    - Trading decision logs
    - Execution confirmations

TODOs:
    - Add support for stop-loss orders
    - Implement trailing stop functionality
    - Add support for multiple trading pairs
    - Implement profit/loss tracking

Dependencies:
    - Python >= 3.8
    - time (standard library)
    - typing (standard library)

Assumptions & Notes:
    - Rules are evaluated on each monitoring cycle
    - Only one rule per price level is executed
    - Balances are verified before each trade
    - Average price is recalculated after each buy
"""

import time  # For monitoring intervals and timing
from typing import Dict, Optional, Set  # For type hints


class TradingBot:
    """
    Implements automated trading logic and execution.
    
    :param: None
    :return: None
    """


    def __init__(self, api_client, account_manager, config, logger=None):
        """
        Initializes the TradingBot.
        
        :param api_client: APIClient instance for API operations
        :param account_manager: AccountManager instance for account operations
        :param config: Configuration object containing trading rules
        :param logger: Optional logger for output
        :return: None
        """
        
        self.api_client = api_client  # Store API client instance
        self.account_manager = account_manager  # Store account manager instance
        self.config = config  # Store configuration
        self.logger = logger  # Store logger instance
        self.executed_rules: Set[str] = set()  # Track executed rules to prevent duplicates
        self.current_average_price: Optional[float] = None  # Cache current average price
        self.is_running = False  # Bot running state


    def log(self, message: str) -> None:
        """
        Logs a message if logger is available.
        
        :param message: Message to log
        :return: None
        """
        
        if self.logger:  # Verify if logger exists
            print(message)  # Print message (redirected to logger via stdout)
        else:  # No logger available
            print(message)  # Print to console


    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Retrieves current market price for a symbol.
        
        :param symbol: Trading pair symbol (e.g., BTC-BRL)
        :return: Current price as float or None if failed
        """
        
        ticker = self.api_client.get_ticker(symbol)  # Get ticker data
        if ticker:  # Verify if ticker retrieved
            last_price = ticker.get("last")  # Get last traded price
            if last_price:  # Verify if price exists
                try:  # Attempt to convert to float
                    return float(last_price)  # Return price as float
                except ValueError:  # Handle conversion error
                    return None  # Return None on error
        return None  # Return None if ticker not available


    def update_average_price(self) -> bool:
        """
        Updates the cached average purchase price.
        
        :param: None
        :return: True if update successful, False otherwise
        """
        
        avg_price = self.account_manager.calculate_average_price(  # Calculate average price
            self.config.CRYPTO,  # Crypto symbol
            self.config.PRIMARY_SYMBOL  # Trading pair
        )
        
        if avg_price is not None:  # Verify if average price calculated
            self.current_average_price = avg_price  # Update cached average price
            return True  # Return success
        return False  # Return failure


    def get_average_price(self) -> Optional[float]:
        """
        Returns the current average purchase price, updating if necessary.
        
        :param: None
        :return: Average price as float or None if unavailable
        """
        
        if self.current_average_price is None:  # Verify if average price not cached
            self.update_average_price()  # Update average price
        return self.current_average_price  # Return cached average price


    def calculate_percentage_difference(self, current_price: float, average_price: float) -> float:
        """
        Calculates percentage difference between current and average price.
        
        :param current_price: Current market price
        :param average_price: Average purchase price
        :return: Percentage difference as decimal (0.10 = 10%)
        """
        
        if average_price == 0:  # Verify for division by zero
            return 0.0  # Return zero if average price is zero
        
        difference = current_price - average_price  # Calculate price difference
        percentage = difference / average_price  # Calculate percentage
        return percentage  # Return percentage difference


    def verify_buy_rules(self, current_price: float, average_price: float) -> Optional[Dict]:
        """
        Evaluates buy rules and returns action if triggered.
        
        :param current_price: Current market price
        :param average_price: Average purchase price
        :return: Dictionary with action details or None if no rule triggered
        """
        
        percentage_diff = self.calculate_percentage_difference(current_price, average_price)  # Calculate percentage difference
        
        rules = self.config.RULES  # Get trading rules
        
        if percentage_diff >= rules.BTC_BUY_THRESHOLD_3:  # Verify threshold 3 (25%)
            rule_key = f"buy_3_{int(average_price)}"  # Generate unique rule key
            if rule_key not in self.executed_rules:  # Verify if rule not already executed
                return {  # Return buy action
                    "action": "buy",  # Action type
                    "reason": f"Price {percentage_diff*100:.2f}% above average (threshold: 25%)",  # Reason
                    "amount_percentage": rules.BTC_BUY_AMOUNT_3,  # Amount to buy (50%)
                    "rule_key": rule_key  # Rule identifier
                }
        
        elif percentage_diff >= rules.BTC_BUY_THRESHOLD_2:  # Verify threshold 2 (20%)
            rule_key = f"buy_2_{int(average_price)}"  # Generate unique rule key
            if rule_key not in self.executed_rules:  # Verify if rule not already executed
                return {  # Return buy action
                    "action": "buy",  # Action type
                    "reason": f"Price {percentage_diff*100:.2f}% above average (threshold: 20%)",  # Reason
                    "amount_percentage": rules.BTC_BUY_AMOUNT_2,  # Amount to buy (20%)
                    "rule_key": rule_key  # Rule identifier
                }
        
        elif percentage_diff >= rules.BTC_BUY_THRESHOLD_1:  # Verify threshold 1 (10%)
            rule_key = f"buy_1_{int(average_price)}"  # Generate unique rule key
            if rule_key not in self.executed_rules:  # Verify if rule not already executed
                return {  # Return buy action
                    "action": "buy",  # Action type
                    "reason": f"Price {percentage_diff*100:.2f}% above average (threshold: 10%)",  # Reason
                    "amount_percentage": rules.BTC_BUY_AMOUNT_1,  # Amount to buy (10%)
                    "rule_key": rule_key  # Rule identifier
                }
        
        return None  # Return None if no buy rule triggered


    def verify_sell_rules(self, current_price: float, average_price: float) -> Optional[Dict]:
        """
        Evaluates sell rules and returns action if triggered.
        
        :param current_price: Current market price
        :param average_price: Average purchase price
        :return: Dictionary with action details or None if no rule triggered
        """
        
        percentage_diff = self.calculate_percentage_difference(current_price, average_price)  # Calculate percentage difference
        
        rules = self.config.RULES  # Get trading rules
        
        if percentage_diff >= rules.BTC_SELL_THRESHOLD:  # Verify sell threshold (100%)
            rule_key = f"sell_{int(average_price)}"  # Generate unique rule key
            if rule_key not in self.executed_rules:  # Verify if rule not already executed
                return {  # Return sell action
                    "action": "sell",  # Action type
                    "reason": f"Price {percentage_diff*100:.2f}% above average (threshold: 100%)",  # Reason
                    "amount_percentage": rules.BTC_SELL_AMOUNT,  # Amount to sell (20%)
                    "rule_key": rule_key  # Rule identifier
                }
        
        return None  # Return None if no sell rule triggered


    def execute_buy(self, amount_percentage: float, rule_key: str) -> bool:
        """
        Executes a buy order for a percentage of available BRL balance.
        
        :param amount_percentage: Percentage of balance to spend (0.10 = 10%)
        :param rule_key: Rule identifier for duplicate prevention
        :return: True if order placed successfully, False otherwise
        """
        
        available_brl = self.account_manager.get_available_balance(self.config.FIAT)  # Get available BRL balance
        
        if available_brl <= 0:  # Verify if balance available
            self.log(f"Insufficient BRL balance: {available_brl}")  # Log insufficient balance
            return False  # Return failure
        
        cost = available_brl * amount_percentage  # Calculate cost to spend
        
        if cost < 10:  # Verify minimum order value
            self.log(f"Order cost too low: {cost} BRL (minimum: 10 BRL)")  # Log low cost
            return False  # Return failure
        
        account_id = self.account_manager.get_account_id()  # Get account ID
        if not account_id:  # Verify if account ID available
            self.log("Account ID not available")  # Log missing account ID
            return False  # Return failure
        
        self.log(f"Executing BUY: {cost:.2f} BRL ({amount_percentage*100:.0f}% of balance)")  # Log buy action
        
        result = self.api_client.place_order(  # Place market buy order
            account_id=account_id,  # Account ID
            symbol=self.config.PRIMARY_SYMBOL,  # Trading pair
            side="buy",  # Buy side
            order_type="market",  # Market order type
            cost=cost  # Cost in BRL
        )
        
        if result:  # Verify if order placed successfully
            order_id = result.get("orderId")  # Get order ID
            self.log(f"Buy order placed successfully. Order ID: {order_id}")  # Log success
            self.executed_rules.add(rule_key)  # Mark rule as executed
            self.update_average_price()  # Update average price after buy
            return True  # Return success
        else:  # Order placement failed
            self.log("Buy order failed")  # Log failure
            return False  # Return failure


    def execute_sell(self, amount_percentage: float, rule_key: str) -> bool:
        """
        Executes a sell order for a percentage of available BTC balance.
        
        :param amount_percentage: Percentage of balance to sell (0.20 = 20%)
        :param rule_key: Rule identifier for duplicate prevention
        :return: True if order placed successfully, False otherwise
        """
        
        available_btc = self.account_manager.get_available_balance(self.config.CRYPTO)  # Get available BTC balance
        
        if available_btc <= 0:  # Verify if balance available
            self.log(f"Insufficient BTC balance: {available_btc}")  # Log insufficient balance
            return False  # Return failure
        
        qty = available_btc * amount_percentage  # Calculate quantity to sell
        
        if qty < 0.00001:  # Verify minimum order quantity
            self.log(f"Order quantity too low: {qty} BTC")  # Log low quantity
            return False  # Return failure
        
        account_id = self.account_manager.get_account_id()  # Get account ID
        if not account_id:  # Verify if account ID available
            self.log("Account ID not available")  # Log missing account ID
            return False  # Return failure
        
        self.log(f"Executing SELL: {qty:.8f} BTC ({amount_percentage*100:.0f}% of balance)")  # Log sell action
        
        result = self.api_client.place_order(  # Place market sell order
            account_id=account_id,  # Account ID
            symbol=self.config.PRIMARY_SYMBOL,  # Trading pair
            side="sell",  # Sell side
            order_type="market",  # Market order type
            qty=str(qty)  # Quantity as string
        )
        
        if result:  # Verify if order placed successfully
            order_id = result.get("orderId")  # Get order ID
            self.log(f"Sell order placed successfully. Order ID: {order_id}")  # Log success
            self.executed_rules.add(rule_key)  # Mark rule as executed
            return True  # Return success
        else:  # Order placement failed
            self.log("Sell order failed")  # Log failure
            return False  # Return failure


def create_trading_bot(api_client, account_manager, config, logger=None) -> TradingBot:
    """
    Factory function to create a TradingBot instance.
    
    :param api_client: APIClient instance for API operations
    :param account_manager: AccountManager instance for account operations
    :param config: Configuration object containing trading rules
    :param logger: Optional logger for output
    :return: Initialized TradingBot instance
    """
    
    return TradingBot(api_client, account_manager, config, logger)  # Create and return TradingBot instance
