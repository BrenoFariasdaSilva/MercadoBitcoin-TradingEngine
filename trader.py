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
