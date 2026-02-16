"""
================================================================================
Mercado Bitcoin Automated Trading Bot
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-16
Description :
    Automated trading bot for Mercado Bitcoin cryptocurrency exchange.
    This bot monitors BTC prices and executes rule-based buy/sell orders
    based on percentage differences from average purchase price.

    Key features include:
        - OAuth2 authentication with Mercado Bitcoin API v4
        - Real-time price monitoring for BTC-BRL and BTC-USD
        - Average purchase price calculation from order history
        - Rule-based automatic buy orders (10%, 20%, 25% thresholds)
        - Rule-based automatic sell orders (100% threshold)
        - Duplicate execution prevention
        - Safe balance verification before orders

Usage:
    1. Set environment variables MB_API_KEY and MB_API_SECRET.
    2. Run the script via Python or Makefile.
        $ python main.py
    3. Bot will continuously monitor and execute trades based on configured rules.

Outputs:
    - ./Logs/main.log — Trading activity and decisions log
    - Market orders executed on Mercado Bitcoin platform

TODOs:
    - Add support for multiple cryptocurrencies
    - Implement stop-loss functionality
    - Add performance metrics and reporting
    - Implement backtesting capabilities

Dependencies:
    - Python >= 3.8
    - requests
    - colorama
    - Logger (custom module)
    - config, auth, api_client, account, trader modules

Assumptions & Notes:
    - API credentials must be set as environment variables
    - Bot runs continuously until stopped manually
    - Only BTC trading is currently implemented
    - Uses market orders for execution
"""

import atexit  # For playing a sound when the program finishes
import datetime  # For getting the current date and time
import os  # For running a command in the terminal
import platform  # For getting the operating system name
import sys  # For system-specific parameters and functions
from account import create_account_manager  # For account management
from api_client import create_api_client  # For API communication
from auth import create_authenticator  # For API authentication
from colorama import Style  # For coloring the terminal
from config import Config, validate_config, get_config_summary  # For configuration management
from Logger import Logger  # For logging output to both terminal and file
from pathlib import Path  # For handling file paths
from trader import create_trading_bot  # For trading logic


# Macros:
class BackgroundColors:  # Colors for the terminal
    CYAN = "\033[96m"  # Cyan
    GREEN = "\033[92m"  # Green
    YELLOW = "\033[93m"  # Yellow
    RED = "\033[91m"  # Red
    BOLD = "\033[1m"  # Bold
    UNDERLINE = "\033[4m"  # Underline
    CLEAR_TERMINAL = "\033[H\033[J"  # Clear the terminal


# Execution Constants:
VERBOSE = False  # Set to True to output verbose messages

# Logger Setup:
logger = Logger(f"./Logs/{Path(__file__).stem}.log", clean=True)  # Create a Logger instance
sys.stdout = logger  # Redirect stdout to the logger
sys.stderr = logger  # Redirect stderr to the logger

# Sound Constants:
SOUND_COMMANDS = {
    "Darwin": "afplay",
    "Linux": "aplay",
    "Windows": "start",
}  # The commands to play a sound for each operating system
SOUND_FILE = "./.assets/Sounds/NotificationSound.wav"  # The path to the sound file

# RUN_FUNCTIONS:
RUN_FUNCTIONS = {
    "Play Sound": True,  # Set to True to play a sound when the program finishes
}

# Functions Definitions:


def verbose_output(true_string="", false_string=""):
    """
    Outputs a message if the VERBOSE constant is set to True.

    :param true_string: The string to be outputted if the VERBOSE constant is set to True.
    :param false_string: The string to be outputted if the VERBOSE constant is set to False.
    :return: None
    """

    if VERBOSE and true_string != "":  # If VERBOSE is True and a true_string was provided
        print(true_string)  # Output the true statement string
    elif false_string != "":  # If a false_string was provided
        print(false_string)  # Output the false statement string


def display_account_balances(account_manager):
    """
    Retrieves and displays account balances.

    :param account_manager: The account manager instance
    :return: None
    """

    print(
        f"{BackgroundColors.GREEN}Retrieving account balances...{Style.RESET_ALL}"
    )  # Output balance retrieval message

    balances = account_manager.get_balances()  # Get account balances
    if balances:  # Verify if balances retrieved
        for balance in balances:  # Iterate through balances
            symbol = balance.get("symbol", "N/A")  # Get symbol
            available = balance.get("available", "0")  # Get available balance
            total = balance.get("total", "0")  # Get total balance
            print(
                f"{BackgroundColors.CYAN}  {symbol}: {BackgroundColors.YELLOW}Available={available}, Total={total}{Style.RESET_ALL}"
            )  # Output balance information


def display_average_price(account_manager):
    """
    Calculates and displays the average BTC purchase price.

    :param account_manager: The account manager instance
    :return: avg_price
    """

    print(
        f"\n{BackgroundColors.GREEN}Calculating average BTC purchase price...{Style.RESET_ALL}"
    )  # Output average price calculation message

    avg_price = account_manager.calculate_average_price(  # Calculate average price
        Config.CRYPTO,  # Crypto symbol
        Config.PRIMARY_SYMBOL  # Trading pair
    )

    if avg_price:  # Verify if average price calculated
        print(
            f"{BackgroundColors.GREEN}Average BTC price: {BackgroundColors.CYAN}{avg_price:.2f} BRL{Style.RESET_ALL}"
        )  # Output average price
    else:  # No average price available
        print(
            f"{BackgroundColors.YELLOW}No BTC purchase history found.{Style.RESET_ALL}"
        )  # Output no history message

    return avg_price


def initialize_trading_bot(api_client, account_manager, logger):
    """
    Initializes the trading bot instance.

    :param api_client: The API client instance
    :param account_manager: The account manager instance
    :param logger: The logger instance
    :return: trading_bot
    """

    print(
        f"\n{BackgroundColors.GREEN}Initializing trading bot...{Style.RESET_ALL}"
    )  # Output trading bot initialization message

    trading_bot = create_trading_bot(  # Create trading bot instance
        api_client,  # API client instance
        account_manager,  # Account manager instance
        Config,  # Configuration
        logger  # Logger instance
    )

    return trading_bot


def display_trading_rules():
    """
    Displays configured trading rules.

    :param: None
    :return: None
    """

    print(
        f"{BackgroundColors.GREEN}Trading rules configured:{Style.RESET_ALL}"
    )  # Output trading rules header
    print(
        f"{BackgroundColors.CYAN}  BUY 10% of BRL when price is 10% above average{Style.RESET_ALL}"
    )  # Output buy rule 1
    print(
        f"{BackgroundColors.CYAN}  BUY 20% of BRL when price is 20% above average{Style.RESET_ALL}"
    )  # Output buy rule 2
    print(
        f"{BackgroundColors.CYAN}  BUY 50% of BRL when price is 25% above average{Style.RESET_ALL}"
    )  # Output buy rule 3
    print(
        f"{BackgroundColors.CYAN}  SELL 20% of BTC when price is 100% above average (double){Style.RESET_ALL}"
    )  # Output sell rule


def start_trading_bot(trading_bot):
    """
    Starts the trading bot loop and handles interrupts and errors.

    :param trading_bot: The trading bot instance
    :return: None
    """

    print(
        f"\n{BackgroundColors.BOLD}{BackgroundColors.GREEN}Starting trading bot... (Press Ctrl+C to stop){Style.RESET_ALL}\n"
    )  # Output bot start message

    try:  # Attempt to run trading bot
        trading_bot.run()  # Start trading bot main loop
    except KeyboardInterrupt:  # Handle keyboard interrupt
        print(
            f"\n{BackgroundColors.YELLOW}Keyboard interrupt received. Stopping bot...{Style.RESET_ALL}"
        )  # Output interrupt message
        trading_bot.stop()  # Stop trading bot
    except Exception as e:  # Catch any other exceptions
        print(
            f"\n{BackgroundColors.RED}Error occurred: {str(e)}{Style.RESET_ALL}"
        )  # Output error message
        trading_bot.stop()  # Stop trading bot


def verify_filepath_exists(filepath):
    """
    Verify if a file or folder exists at the specified path.

    :param filepath: Path to the file or folder
    :return: True if the file or folder exists, False otherwise
    """

    verbose_output(
        f"{BackgroundColors.GREEN}Verifying if the file or folder exists at the path: {BackgroundColors.CYAN}{filepath}{Style.RESET_ALL}"
    )  # Output the verbose message

    return os.path.exists(filepath)  # Return True if the file or folder exists, False otherwise


def to_seconds(obj):
    """
    Converts various time-like objects to seconds.
    
    :param obj: The object to convert (can be int, float, timedelta, datetime, etc.)
    :return: The equivalent time in seconds as a float, or None if conversion fails
    """
    
    if obj is None:  # None can't be converted
        return None  # Signal failure to convert
    if isinstance(obj, (int, float)):  # Already numeric (seconds or timestamp)
        return float(obj)  # Return as float seconds
    if hasattr(obj, "total_seconds"):  # Timedelta-like objects
        try:  # Attempt to call total_seconds()
            return float(obj.total_seconds())  # Use the total_seconds() method
        except Exception:
            pass  # Fallthrough on error
    if hasattr(obj, "timestamp"):  # Datetime-like objects
        try:  # Attempt to call timestamp()
            return float(obj.timestamp())  # Use timestamp() to get seconds since epoch
        except Exception:
            pass  # Fallthrough on error
    return None  # Couldn't convert


def calculate_execution_time(start_time, finish_time=None):
    """
    Calculates the execution time and returns a human-readable string.

    Accepts either:
    - Two datetimes/timedeltas: `calculate_execution_time(start, finish)`
    - A single timedelta or numeric seconds: `calculate_execution_time(delta)`
    - Two numeric timestamps (seconds): `calculate_execution_time(start_s, finish_s)`

    Returns a string like "1h 2m 3s".
    """

    if finish_time is None:  # Single-argument mode: start_time already represents duration or seconds
        total_seconds = to_seconds(start_time)  # Try to convert provided value to seconds
        if total_seconds is None:  # Conversion failed
            try:  # Attempt numeric coercion
                total_seconds = float(start_time)  # Attempt numeric coercion
            except Exception:
                total_seconds = 0.0  # Fallback to zero
    else:  # Two-argument mode: Compute difference finish_time - start_time
        st = to_seconds(start_time)  # Convert start to seconds if possible
        ft = to_seconds(finish_time)  # Convert finish to seconds if possible
        if st is not None and ft is not None:  # Both converted successfully
            total_seconds = ft - st  # Direct numeric subtraction
        else:  # Fallback to other methods
            try:  # Attempt to subtract (works for datetimes/timedeltas)
                delta = finish_time - start_time  # Try subtracting (works for datetimes/timedeltas)
                total_seconds = float(delta.total_seconds())  # Get seconds from the resulting timedelta
            except Exception:  # Subtraction failed
                try:  # Final attempt: Numeric coercion
                    total_seconds = float(finish_time) - float(start_time)  # Final numeric coercion attempt
                except Exception:  # Numeric coercion failed
                    total_seconds = 0.0  # Fallback to zero on failure

    if total_seconds is None:  # Ensure a numeric value
        total_seconds = 0.0  # Default to zero
    if total_seconds < 0:  # Normalize negative durations
        total_seconds = abs(total_seconds)  # Use absolute value

    days = int(total_seconds // 86400)  # Compute full days
    hours = int((total_seconds % 86400) // 3600)  # Compute remaining hours
    minutes = int((total_seconds % 3600) // 60)  # Compute remaining minutes
    seconds = int(total_seconds % 60)  # Compute remaining seconds

    if days > 0:  # Include days when present
        return f"{days}d {hours}h {minutes}m {seconds}s"  # Return formatted days+hours+minutes+seconds
    if hours > 0:  # Include hours when present
        return f"{hours}h {minutes}m {seconds}s"  # Return formatted hours+minutes+seconds
    if minutes > 0:  # Include minutes when present
        return f"{minutes}m {seconds}s"  # Return formatted minutes+seconds
    return f"{seconds}s"  # Fallback: only seconds


def play_sound():
    """
    Plays a sound when the program finishes and skips if the operating system is Windows.

    :param: None
    :return: None
    """

    current_os = platform.system()  # Get the current operating system
    if current_os == "Windows":  # If the current operating system is Windows
        return  # Do nothing

    if verify_filepath_exists(SOUND_FILE):  # If the sound file exists
        if current_os in SOUND_COMMANDS:  # If the platform.system() is in the SOUND_COMMANDS dictionary
            os.system(f"{SOUND_COMMANDS[current_os]} {SOUND_FILE}")  # Play the sound
        else:  # If the platform.system() is not in the SOUND_COMMANDS dictionary
            print(
                f"{BackgroundColors.RED}The {BackgroundColors.CYAN}{current_os}{BackgroundColors.RED} is not in the {BackgroundColors.CYAN}SOUND_COMMANDS dictionary{BackgroundColors.RED}. Please add it!{Style.RESET_ALL}"
            )
    else:  # If the sound file does not exist
        print(
            f"{BackgroundColors.RED}Sound file {BackgroundColors.CYAN}{SOUND_FILE}{BackgroundColors.RED} not found. Make sure the file exists.{Style.RESET_ALL}"
        )


def main():
    """
    Main function.

    :param: None
    :return: None
    """

    print(
        f"{BackgroundColors.CLEAR_TERMINAL}{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}Mercado Bitcoin Trading Bot{BackgroundColors.GREEN} program!{Style.RESET_ALL}",
        end="\n\n",
    )  # Output the welcome message
    start_time = datetime.datetime.now()  # Get the start time of the program

    verbose_output(
        f"{BackgroundColors.GREEN}Validating configuration...{Style.RESET_ALL}"
    )  # Output configuration validation message

    if not validate_config():  # Verify if configuration is valid
        print(
            f"{BackgroundColors.RED}Configuration validation failed!{Style.RESET_ALL}"
        )  # Output error message
        print(
            f"{BackgroundColors.RED}Please set MB_API_KEY and MB_API_SECRET environment variables.{Style.RESET_ALL}"
        )  # Output instructions
        return  # Exit if configuration invalid

    display_configuration_summary()  # Show configuration summary

    authenticator = initialize_authenticator()  # Initialize authenticator
    if not authenticator:  # Verify if authentication successful
        return  # Exit if authentication failed

    api_client = initialize_api_client(authenticator)  # Initialize API client

    account_manager, account_id = initialize_account_manager(api_client)  # Initialize account manager
    if not account_id:  # Verify if account ID retrieved
        return  # Exit if account ID not available

    display_account_balances(account_manager)  # Show account balances

    avg_price = display_average_price(account_manager)  # Calculate and display average price

    trading_bot = initialize_trading_bot(api_client, account_manager, logger)  # Initialize trading bot

    display_trading_rules()  # Show trading rules

    start_trading_bot(trading_bot)  # Start the trading bot loop

    finish_time = datetime.datetime.now()  # Get the finish time of the program
    print(
        f"\n{BackgroundColors.GREEN}Start time: {BackgroundColors.CYAN}{start_time.strftime('%d/%m/%Y - %H:%M:%S')}\n{BackgroundColors.GREEN}Finish time: {BackgroundColors.CYAN}{finish_time.strftime('%d/%m/%Y - %H:%M:%S')}\n{BackgroundColors.GREEN}Execution time: {BackgroundColors.CYAN}{calculate_execution_time(start_time, finish_time)}{Style.RESET_ALL}"
    )  # Output the start and finish times
    print(
        f"\n{BackgroundColors.BOLD}{BackgroundColors.GREEN}Program finished.{Style.RESET_ALL}"
    )  # Output the end of the program message
    (
        atexit.register(play_sound) if RUN_FUNCTIONS["Play Sound"] else None
    )  # Register the play_sound function to be called when the program finishes


if __name__ == "__main__":
    """
    This is the standard boilerplate that calls the main() function.

    :return: None
    """

    main()  # Call the main function
