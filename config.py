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

