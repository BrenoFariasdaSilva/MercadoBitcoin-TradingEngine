<div align="center">
  
# [MercadoBitcoin-Trading Engine.](https://github.com/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine) <img src="https://github.com/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine/blob/main/.assets/Icons/Bitcoin.svg"  width="3%" height="3%">

</div>

<div align="center">
  
---

Project-Description.
  
---

</div>

<div align="center">

![GitHub Code Size in Bytes](https://img.shields.io/github/languages/code-size/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine)
![GitHub Commits](https://img.shields.io/github/commit-activity/t/BrenoFariasDaSilva/MercadoBitcoin-TradingEngine/main)
![GitHub Last Commit](https://img.shields.io/github/last-commit/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine)
![GitHub Forks](https://img.shields.io/github/forks/BrenoFariasDaSilva/MercadoBitcoin-TradingEngine)
![GitHub Language Count](https://img.shields.io/github/languages/count/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine)
![GitHub License](https://img.shields.io/github/license/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine)
![GitHub Stars](https://img.shields.io/github/stars/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine)
![GitHub Contributors](https://img.shields.io/github/contributors/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine)
![GitHub Created At](https://img.shields.io/github/created-at/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine)
![wakatime](https://wakatime.com/badge/github/BrenoFariasdaSilva/MercadoBitcoin-TradingEngine.svg)

</div>

<div align="center">
  
![RepoBeats Statistics](https://repobeats.axiom.co/api/embed/7be789b2f02db4e7c76ee626ed7d577423834a01.svg "Repobeats analytics image")

</div>

## Table of Contents
- [MercadoBitcoin-Trading Engine. ](#mercadobitcoin-trading-engine-)
	- [Table of Contents](#table-of-contents)
	- [Introduction](#introduction)
	- [Requirements](#requirements)
	- [Setup](#setup)
		- [Clone the repository](#clone-the-repository)
	- [Installation:](#installation)
	- [Environment variables and `.env` template](#environment-variables-and-env-template)
	- [Run Programing Language Code:](#run-programing-language-code)
		- [Dependencies](#dependencies)
		- [Dataset - Optional](#dataset---optional)
	- [Usage](#usage)
	- [Contributing](#contributing)
	- [Collaborators](#collaborators)
	- [License](#license)
		- [Apache License 2.0](#apache-license-20)

## Introduction

This repository contains an automated trading bot for the Mercado Bitcoin exchange implemented in Python. The implementation is organized into modules that together perform authentication, API communication, account management, trading decision logic and logging. The code targets Python >= 3.8 and uses Mercado Bitcoin HTTP API v4 endpoints described below.

Module documentation (responsibilities, exported classes and public functions, interactions):

- `config.py`
  - Responsibility: centralizes runtime configuration constants and trading rules.
  - Classes:
    - `TradingRules` — trading thresholds and allocation percentages.
    - `APIConfig` — API constants: `BASE_URL`, `TIMEOUT`, `MAX_RETRIES`, `RETRY_DELAY`.
    - `MonitoringConfig` — monitoring constants: `VERIFICATION_INTERVAL`, `SYMBOLS_TO_MONITOR`, `PRIMARY_SYMBOL`, `CRYPTO_SYMBOL`, `FIAT_SYMBOL`.
    - `Config` — aggregated configuration class exposing values and reading environment variables `MB_API_KEY`, `MB_API_SECRET` (default empty string).
  - Public functions:
    - `validate_config() -> bool` — returns `True` only if `Config.API_KEY`, `Config.API_SECRET` and `Config.BASE_URL` are present.
    - `get_config_summary() -> dict` — returns a non-sensitive summary of selected `Config` values.
  - Interaction: consumed by `main.py` and passed to `TradingBot` and `APIClient`.

- `auth.py`
  - Responsibility: performs OAuth2 client-credentials authentication and provides authorization headers.
  - Classes:
    - `Authenticator(api_key: str, api_secret: str, base_url: str)`
      - Methods:
        - `authenticate() -> bool` — POSTs to `${base_url}/oauth2/token` with `grant_type=client_credentials` using HTTP Basic auth; stores `access_token`, `token_type` and `token_expiry` (expires_in minus 300s buffer).
        - `is_token_valid() -> bool` — `True` when token exists and not expired.
        - `ensure_authenticated() -> bool` — ensures valid token or re-authenticates.
        - `get_auth_headers() -> Dict[str, str]` — returns `{"Authorization": "{token_type} {access_token}"}` or `{}` if auth fails.
        - `get_access_token() -> Optional[str]` — returns token or `None`.
  - Authentication specifics: uses HTTP Basic auth to request an access token from `${BASE_URL}/oauth2/token` with `grant_type=client_credentials`. Tokens are stored in memory. No nonce or timestamp signing is used — authentication relies on the bearer token.
  - Interaction: used by `APIClient` to add bearer authorization headers to authenticated requests.

- `api_client.py`
  - Responsibility: HTTP client wrapper for Mercado Bitcoin v4 with retry logic and automatic re-authentication on 401.
  - Classes:
    - `APIClient(authenticator, base_url: str, timeout: int = 30, max_retries: int = 3, retry_delay: int = 2)`
      - Public methods (signatures and return types):
        - `make_request(method: str, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None, authenticated: bool = True) -> Optional[dict]`
        - `get_accounts() -> Optional[List[dict]]` — GET `/accounts`.
        - `get_balances(account_id: str) -> Optional[List[dict]]` — GET `/accounts/{account_id}/balances`.
        - `get_ticker(symbol: str) -> Optional[dict]` — GET `/{symbol}/ticker` (unauthenticated).
        - `get_tickers() -> Optional[List[dict]]` — GET `/tickers` (unauthenticated).
        - `get_orderbook(symbol: str) -> Optional[dict]` — GET `/{symbol}/orderbook` (unauthenticated).
        - `get_orders(account_id: str, symbol: str) -> Optional[List[dict]]` — GET `/accounts/{account_id}/{symbol}/orders`.
        - `get_all_orders(account_id: str) -> Optional[dict]` — GET `/accounts/{account_id}/orders`.
        - `get_order(account_id: str, symbol: str, order_id: str) -> Optional[dict]` — GET `/accounts/{account_id}/{symbol}/orders/{order_id}`.
        - `place_order(account_id: str, symbol: str, side: str, order_type: str, qty: Optional[str] = None, cost: Optional[float] = None, limit_price: Optional[float] = None) -> Optional[dict]` — POST `/accounts/{account_id}/{symbol}/orders`.
        - `cancel_order(account_id: str, symbol: str, order_id: str) -> Optional[dict]` — DELETE `/accounts/{account_id}/{symbol}/orders/{order_id}`.
        - `get_positions(account_id: str) -> Optional[List[dict]]` — GET `/accounts/{account_id}/positions`.
        - `get_executions(account_id: str, symbol: str, order_id: str) -> Optional[List[dict]]` — returns `order['executions']` when present.
  - HTTP behavior: `make_request` sets `Content-Type: application/json`, merges `authenticator.get_auth_headers()` for authenticated requests, treats HTTP 200 as success (returns parsed JSON), re-authenticates on 401 when `authenticated=True`, and retries other failures up to `max_retries` using `retry_delay`.

- `account.py`
  - Responsibility: account selection, balance queries and average price calculation from executed trades.
  - Classes:
    - `AccountManager(api_client)`
      - Methods and return types:
        - `get_accounts() -> Optional[List[dict]]` — caches and returns accounts list.
        - `get_account_id() -> Optional[str]` — returns or sets the first account id.
        - `set_account_id(account_id: str) -> None`.
        - `get_balances() -> Optional[List[dict]]`.
        - `get_balance(symbol: str) -> Optional[dict]`.
        - `get_available_balance(symbol: str) -> float` — returns `float` or `0.0`.
        - `get_total_balance(symbol: str) -> float` — returns `float` or `0.0`.
        - `get_all_orders() -> Optional[dict]`.
        - `get_orders_for_symbol(symbol: str) -> Optional[List[dict]]`.
        - `calculate_average_price(crypto_symbol: str, trading_pair: str) -> Optional[float]` — computes weighted average from buy executions in `/accounts/{account_id}/orders` response (expects `items` list and per-order `executions`).
        - `get_positions() -> Optional[List[dict]]`.
  - Interaction: used by `main.py` for display and by `TradingBot` for balance checks and average price computation.

- `trader.py`
  - Responsibility: rule-based trading logic and order execution.
  - Classes:
    - `TradingBot(api_client, account_manager, config, logger=None)`
      - Public methods:
        - `log(message: str) -> None` — prints to stdout (redirected by `main.py` to `Logger`).
        - `get_current_price(symbol: str) -> Optional[float]` — reads `ticker['last']` and returns `float`.
        - `update_average_price() -> bool` — updates cached average price from `AccountManager.calculate_average_price`.
        - `get_average_price() -> Optional[float]` — returns cached average price, updating if needed.
        - `calculate_percentage_difference(current_price: float, average_price: float) -> float` — returns decimal percentage difference.
        - `verify_buy_rules(current_price: float, average_price: float) -> Optional[dict]` — checks three buy thresholds and returns an action dict when triggered.
        - `verify_sell_rules(current_price: float, average_price: float) -> Optional[dict]` — checks sell threshold and returns an action dict when triggered.
        - `execute_buy(amount_percentage: float, rule_key: str) -> bool` — checks available BRL, enforces minimum order value (10 BRL), places a market buy using `cost` field.
        - `execute_sell(amount_percentage: float, rule_key: str) -> bool` — checks available BTC, enforces minimum quantity (0.00001 BTC), places a market sell using `qty` field.
        - `evaluate_and_execute() -> None` — orchestrates price retrieval, rule evaluation and execution.
        - `run_cycle() -> None` — calls `evaluate_and_execute()` and logs exceptions.
        - `run() -> None` — main loop: calls `run_cycle()` then sleeps `config.VERIFICATION_INTERVAL` seconds.
        - `stop() -> None` — stops the loop.
  - Trading rules (exact implementation):
    - Buy thresholds (current price above weighted average purchase price):
      - 10% (`TradingRules.BTC_BUY_THRESHOLD_1 = 0.10`) → buy 10% of available BRL (`BTC_BUY_AMOUNT_1 = 0.10`).
      - 20% (`TradingRules.BTC_BUY_THRESHOLD_2 = 0.20`) → buy 20% of available BRL (`BTC_BUY_AMOUNT_2 = 0.20`).
      - 25% (`TradingRules.BTC_BUY_THRESHOLD_3 = 0.25`) → buy 50% of available BRL (`BTC_BUY_AMOUNT_3 = 0.50`).
    - Sell threshold:
      - 100% (`TradingRules.BTC_SELL_THRESHOLD = 1.00`) → sell 20% of available BTC (`BTC_SELL_AMOUNT = 0.20`).
  - Duplicate-execution protection: triggered actions are assigned `rule_key` strings like `buy_1_{int(average_price)}` or `sell_{int(average_price)}` and stored in `self.executed_rules` after successful execution; this prevents re-executing the same rule for the same integer average-price bucket.

- `Logger.py`
  - Responsibility: dual-channel logger that mirrors console output to a sanitized log file while preserving color to the terminal when supported.
  - Classes:
    - `Logger(logfile_path, clean=False)` with `write(message)`, `flush()` and `close()`.
  - Behavior: strips ANSI escape sequences for file output using regex `\x1B\[[0-9;]*[a-zA-Z]`. `main.py` replaces `sys.stdout`/`sys.stderr` with `Logger` writing to `./Logs/main.log`.

- `main.py`
  - Responsibility: program entry point, validation, initialization and orchestration of the components above.
  - Key steps performed by `main()`:
    - Validates `Config` (requires `MB_API_KEY` and `MB_API_SECRET`).
    - Initializes `Authenticator`, `APIClient`, `AccountManager`, prints balances and average BTC price, creates `TradingBot` and starts the trading loop (`trading_bot.run()`).
    - Provides utility helpers: `display_configuration_summary()`, `display_trading_rules()`, `display_account_balances()`, `calculate_execution_time()`, `play_sound()` (skipped on Windows).

## Requirements

- Python 3.8 or higher.
- The code reads API credentials from environment variables at runtime. A template is provided in `.env.example`.
  - `MB_API_KEY` — API key for Mercado Bitcoin (required).
  - `MB_API_SECRET` — API secret for Mercado Bitcoin (required).
- Default API base URL: `https://api.mercadobitcoin.net/api/v4` (set in `config.APIConfig.BASE_URL`).
- Network connectivity is required to reach the API endpoints and to authenticate.
