"""
auth.py - Authentication Module
Handles user login, registration, and validation functions for the Twitter-like application.
"""
import getpass

class Auth:
    """
    Authentication handler for user login and registration operations.
    Provides methods for password input, email validation, and user registration.
    """
    
    def __init__(self, database, utils):
        """
        Initialize the authentication handler.
        
        Args:
            database: Database object for executing queries
            utils: Utils object for common utility functions
        """
        self.db = database
        self.utils = utils

    @staticmethod
    def hide_password():
        """
        Get password input without displaying characters on screen.
        Uses getpass module for secure password entry.
        
        Returns:
            str: Password string entered by user
        """
        return getpass.getpass("Password: ")
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format according to basic requirements.
        Email must contain @ and . characters and follow standard format.
        
        Args:
            email (str): Email string to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        if len(email) > 50 or len(email) < 3:
            print("Email must be between 3 and 50 characters long")
            return False
        
        if '@' not in email or '.' not in email:
            print("Email must contain '@' and '.'")
            return False
        
        parts = email.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            print("Email must have text before and after '@'")
            return False
    
        domain_parts = parts[1].split('.')
        if len(domain_parts) < 2 or not domain_parts[0] or not domain_parts[-1]:
            print("Email domain must have text before and after '.'")
            return False
        
        return True

    def generate_user_id(self):
        """
        Generate a unique user ID for a new user by finding the maximum ID and adding 1.
        
        Returns:
            str: New unique user ID
        """
        max_id = self.db.get_max_id("users", "usr")
        return str(max_id + 1)
    
    def login(self):
        """
        Prompt for user credentials and authenticate against the database.
        Uses parameterized queries to prevent SQL injection attacks.
        
        Returns:
            str: User ID if login successful, None otherwise
        """
        print("\n=== User Login ===")
        user_id = self.utils.safe_input("User ID: ")
        password = self.hide_password()
        
        # Use parameterized query to prevent SQL injection
        query = "SELECT usr, name FROM users WHERE usr = ? AND pwd = ?"
        result = self.db.execute_read_query(query, (user_id, password))
        
        if result and len(result) > 0:
            print(f"\nWelcome back, {result[0][1]}!")
            return result[0][0]  # Return the user ID
        else:
            print("\nInvalid credentials. Please try again.")
            self.utils.wait_for_user()
            return None
        
    def validate_register_input(self, input_type, limit, reg_input = "No Input Given"):
        """
        Validate user registration inputs based on length constraints.
        
        Args:
            input_type (str): Type of input being validated (for error messages)
            limit (int): Maximum length limit
            reg_input (str): Input string to validate
            
        Returns:
            bool: True if input is valid, False otherwise
        """
        if len(reg_input) < limit and len(reg_input) >= 1:
            return True
        print(f"Length of {input_type} must be greater than 1 but less than {limit}")
        return False
        
    def register(self):
        """
        Register a new user with validated information.
        Collects and validates user details before creating a new account.
        
        Returns:
            str: New user ID if registration successful, None otherwise
        """
        print("\n=== Create New Account ===")
        
        # Get and validate user name
        while True:
            name = self.utils.safe_input("Enter your name: ")
            if self.validate_register_input("name", 50, name):
                break
    
        # Get and validate email
        while True:
            email = self.utils.safe_input("Enter your email: ")
            if self.validate_email(email):
                break
        
        # Get and validate phone number
        while True:
            phone = self.utils.safe_input("Enter your phone number: ")
            digit_check = 0
            for char in phone:
                if not char.isdigit():
                    digit_check = 1
            if digit_check != 0:
                print("Phone number can only contain digits 0-9")
                continue
            if self.validate_register_input("phone number", 15, phone):
                break
        
        # Get and validate phone number
        while True:
            password = self.hide_password()
            if self.validate_register_input("password", 20, password):
                break
        
        # Generate a unique user ID
        new_user_id = self.generate_user_id()
        
        # Check if email inputted is already registered
        if self.check_email_registered(email):
            print(f"Email {email} is already registered, please use a different email or login")
            self.utils.wait_for_user()
            return None
        
        # Insert new user into database
        query = """
        INSERT INTO users (usr, name, email, phone, pwd)
        VALUES (?, ?, ?, ?, ?)
        """
        
        if self.db.execute_query(query, (new_user_id, name, email, phone, password)):
            print(f"\nAccount created successfully! Your user ID is: {new_user_id}")
            return new_user_id
        else:
            print("\nError creating account. Please try again.")
            self.utils.wait_for_user()
            return None
        
    def check_email_registered(self, email):
        """
        Check if an email is already registered in the database.
        Case-insensitive comparison is used.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if email is already registered, False otherwise
        """
        query = """
        SELECT COUNT(*) FROM users
        WHERE LOWER(email) = LOWER(?)
        """

        result = self.db.execute_read_query(query, (email,))
        return result and result[0][0] > 0