"""
================================================================================
Mercado Bitcoin Trading Bot - Configuration Module
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-16
Description :
    Configuration module for the Mercado Bitcoin trading bot.
    This module centralizes all configuration settings including API credentials,
    trading parameters, monitoring intervals, and trading rules.

    Key features include:
        - API credentials management via environment variables
        - Base URL and endpoint configuration
        - Trading rule definitions for BTC
        - Monitoring and execution parameters
        - Configurable logging levels
        - Safety thresholds and limits

Usage:
    1. Set environment variables MB_API_KEY and MB_API_SECRET before running.
    2. Import this module to access configuration constants.
        from config import Config
    3. Access configuration via Config class attributes.

Outputs:
    - No direct outputs (configuration only)

TODOs:
    - Add support for multiple cryptocurrencies beyond BTC
    - Implement dynamic rule configuration via external file
    - Add support for testnet/sandbox environment

Dependencies:
    - Python >= 3.8
    - os (standard library)

Assumptions & Notes:
    - API credentials must be set as environment variables
    - Default values are used if environment variables are not set
    - All percentage values are in decimal format (0.10 = 10%)
"""

import os  # For accessing environment variables


# Classes Definitions:


class TradingRules:
    """
    Trading rules for BTC operations.
    
    :param: None
    :return: None
    """
    
    BTC_BUY_THRESHOLD_1 = 0.10  # 10% above average price triggers buy of 10% BRL balance
    BTC_BUY_AMOUNT_1 = 0.10  # Buy 10% of available BRL balance
    
    BTC_BUY_THRESHOLD_2 = 0.20  # 20% above average price triggers buy of 20% BRL balance
    BTC_BUY_AMOUNT_2 = 0.20  # Buy 20% of available BRL balance
    
    BTC_BUY_THRESHOLD_3 = 0.25  # 25% above average price triggers buy of 50% BRL balance
    BTC_BUY_AMOUNT_3 = 0.50  # Buy 50% of available BRL balance
    
    BTC_SELL_THRESHOLD = 1.00  # 100% above average price (double) triggers sell
    BTC_SELL_AMOUNT = 0.20  # Sell 20% of BTC position


class APIConfig:  # API configuration constants
    """
    API configuration for Mercado Bitcoin.
    
    :param: None
    :return: None
    """
    
    BASE_URL = "https://api.mercadobitcoin.net/api/v4"  # Base URL for API v4
    TIMEOUT = 30  # Request timeout in seconds
    MAX_RETRIES = 3  # Maximum number of retries for failed requests
    RETRY_DELAY = 2  # Delay between retries in seconds

