"""
utils.py - Utility Module
Provides general utility functions for the Twitter-like application.
Includes screen clearing, menu display, input handling and pagination support.
"""
import platform
import subprocess
from datetime import datetime

class ExitRequestException(Exception):
    """
    Custom exception to signal an exit request from any input point.
    Used for flow control to allow user to exit from any prompt.
    
    Citations:
    1. Implementation inspired by GeeksforGeeks article on custom exceptions
       URL: https://www.geeksforgeeks.org/define-custom-exceptions-in-python/
       Date accessed: March 16, 2025
    
    2. Using exceptions for control flow instead of sys.exit() inspired by Reddit post
       URL: https://www.reddit.com/r/pythontips/comments/d0aysf/dont_use_sysexit1_raise_an_exception_or_assert/
       Date accessed: March 16, 2025
    """
    pass


class Utils:
    """
    Common utility functions used throughout the application.
    Provides methods for UI interaction, formatting, and pagination.
    """

    EXIT_KEYWORD = "!exit"
    
    @staticmethod
    def get_formatted_date():
        """
        Get formatted current date suitable for database storage.
        
        Returns:
            str: Current date as string in YYYY-MM-DD format
        """
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def get_formatted_time():
        """
        Get formatted current time suitable for database storage.
        
        Returns:
            str: Current time as string in HH:MM:SS format
        """
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def wait_for_user():
        """
        Pause execution until user presses Enter.
        
        Raises:
            ExitRequestException: If user enters the exit keyword
        """
        Utils.safe_input("\nPress Enter to continue...")
    
    @staticmethod
    def clear_screen():
        """
        Clear terminal display for better readability.
        Compatible with Windows, macOS, and Linux operating systems.
        """
        system_name = platform.system().lower()
        
        if system_name == 'windows':
            # Windows uses 'cls' command
            subprocess.call('cls', shell=True)
        else:
            # Unix-based systems (macOS, Linux) use 'clear' command
            subprocess.call('clear', shell=True)

    @staticmethod
    def format_heading(heading_text):
        """
        Format a heading with decorative elements.
        
        Args:
            heading_text (str): Text for the heading
        
        Returns:
            str: Formatted heading string
        """
        return f"\n=== {heading_text} ==="
    
    @staticmethod
    def display_menu(title, options_list):
        """
        Display a formatted menu with numbered options.
        
        Args:
            title (str): Menu title
            options_list (list): List of option descriptions
        """
        print(Utils.format_heading(title))
        
        for idx, option_text in enumerate(options_list, 1):
            print(f"{idx}. {option_text}")
    
    @staticmethod
    def get_valid_input(min_value, max_value, prompt=None):
        """
        Get and validate numeric input from the user within a specified range.
        
        Args:
            min_value (int): Minimum valid value
            max_value (int): Maximum valid value
            prompt (str, optional): Custom prompt text
            
        Returns:
            int: Validated integer choice within range
            
        Raises:
            ExitRequestException: If user enters the exit keyword
        """
        if prompt is None:
            prompt = f"\nEnter your choice ({min_value}-{max_value}): "
            
        while True:
            try:
                user_input = Utils.safe_input(prompt)
                user_input = int(user_input)
                if min_value <= user_input <= max_value:
                    return user_input
                print(f"Invalid choice. Please enter a number between {min_value} and {max_value}.")
            except ValueError:
                print("Please enter a numeric value.")
    
    @staticmethod
    def handle_pagination(get_data_func, display_func, id_param=None, empty_message="No items found.",
                          no_more_message="No more items to display.",
                          prompt="View more? (n: next page, p: previous page, q: quit, or enter item number for more details): ",
                          page_size=5):
        """
        Generic pagination handler for displaying data in pages.
        Used for tweets, users, followers, etc.

        Args:
            get_data_func (function): Function to get data with offset parameter
            display_func (function): Function to display the data
            id_param (str, optional): ID parameter to pass to get_data_func
            empty_message (str): Message to display when no items are found
            no_more_message (str): Message to display when no more items are available
            prompt (str): Prompt for user input
            page_size (int): Number of items per page
        
        Returns:
            tuple: (selected_item, action) where action can be 'select', 'quit', or None
            
        Raises:
            ExitRequestException: If user enters the exit keyword
        """
        offset = 0

        while True:
            data = get_data_func(id_param, offset, page_size) if id_param else get_data_func(offset, page_size)

            has_data = display_func(data)

            if not has_data:
                if offset == 0:
                    print(f"\n{empty_message}")
                else:
                    print(f"\n{no_more_message}")
                Utils.wait_for_user()
                return None, 'quit'
            
            action = Utils.safe_input(f"\n{prompt}").lower()

            if action == 'n':
                offset += page_size
            elif action == 'p':
                offset = max(0, offset - page_size)
                if offset == 0:
                    print("\nYou are at the first page.")
            elif action == 'q':
                return None, 'quit'
            else:
                try:
                    item_index = int(action) - 1
                    if 0 <= item_index < len(data):
                        return data[item_index], 'select'
                    else:
                        print("Invalid item number.")
                    Utils.wait_for_user()
                except ValueError:
                    print("Invalid input. Please try again.")
                    Utils.wait_for_user()

    @staticmethod
    def safe_input(prompt):
        """
        Get user input with exit keyword detection.
        
        Args:
            prompt (str): Prompt to display to the user
            
        Returns:
            str: User input string
            
        Raises:
            ExitRequestException: If user enters the exit keyword
        """
        user_input = input(prompt)
        if user_input.lower() == Utils.EXIT_KEYWORD.lower():
            print("\nExit requested. Returning to main menu...")
            raise ExitRequestException("User requested exit")
        return user_input
    