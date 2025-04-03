"""
list_operations.py - Favorite Lists Module
Provides functionality for managing user favorite lists in the Twitter-like application.
"""

class ListOperations:
    """
    Handles operations related to user favorite lists.
    Provides methods for creating, displaying, and managing favorite lists and their contents.
    """
    def __init__(self, database, utils):
        """
        Initialize the list operations handler.
        
        Args:
            database: Database object for executing queries
            utils: Utils object for common utility functions
        """
        self.db = database
        self.utils = utils
    
    def get_favorite_lists(self, user_id):
        """
        Get all favorite lists for a user.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            list: List of favorite list names for the user
        """
        query = "SELECT lname FROM lists WHERE owner_id = ?"
        return self.db.execute_read_query(query, (user_id,))

    def get_list_contents(self, user_id, list_name):
        """
        Get the contents (tweet IDs) of a specific favorite list.
        
        Args:
            user_id (str): ID of the user
            list_name (str): Name of the favorite list
            
        Returns:
            list: List of tweet IDs in the favorite list
        """
        query = "SELECT tid FROM include WHERE owner_id = ? AND lname = ?"
        return self.db.execute_read_query(query, (user_id, list_name))

    def display_favorite_lists(self, user_id):
        """
        Display all favorite lists and their contents for a user.
        Shows list names and the tweet IDs in each list.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            bool: True if user has favorite lists, False otherwise
        """
        lists = self.get_favorite_lists(user_id)

        if not lists:
            print("\nYou have no favorite lists")
            return False

        print("\n=== Your Favorite Lists ===")
        for i, list_item in enumerate(lists, 1):
            list_name = list_item[0]
            contents = self.get_list_contents(user_id, list_name)     

            tid_list = ", ".join([str(item[0]) for item in contents]) if contents else "Empty"

            print(f"{i}. {list_name}: {tid_list}")

        return True              
    
    def add_tweet_to_list(self, user_id, fav_list=None, tweet_id=None):
        """
        Add a tweet to a favorite list.
        If no list is specified, allows user to select from their lists.
        
        Args:
            user_id (str): ID of the user
            fav_list (str, optional): Name of the favorite list
            tweet_id (str, optional): ID of the tweet to add
            
        Returns:
            bool: True if tweet was added successfully, False otherwise
        """
        tweet_exists_query = """
            SELECT EXISTS(
                SELECT 1
                FROM tweets
                WHERE tid = ?
            )
        """
        # Check if tweet exists
        tweet_exists_result = self.db.execute_read_query(tweet_exists_query, (tweet_id,))
        
        if not tweet_exists_result or tweet_exists_result[0][0] == 0:
            print("That tweet doesn't exist!")
            return False
        
        lists_query = """
            SELECT lname
            FROM lists
            WHERE owner_id = ?
        """
        user_lists = self.db.execute_read_query(lists_query, (user_id,))

        if not user_lists:
            print("You have no lists to add to!")
            return False
        
        # If list not specified, prompt user to select one
        if fav_list is None:
            print("Which list would you like to add to?")
            for i, list_item in enumerate(user_lists, 1):
                print(f"{i}. {list_item[0]}")
                
            try:
                choice = int(self.utils.safe_input("\nEnter list number: ")) - 1
                if 0 <= choice < len(user_lists):
                    fav_list = user_lists[choice][0]
                else:
                    print("Invalid list selection.")
                    return False
            except ValueError:
                print("Please enter a valid number.")
                return False
            
        check_tweet_query = """
        SELECT COUNT(*) FROM include 
        WHERE owner_id = ? AND lname = ? AND tid = ?
        """
        tweet_result = self.db.execute_read_query(check_tweet_query, (user_id, fav_list, tweet_id))
        
        if tweet_result and tweet_result[0][0] > 0:
            print(f"Tweet {tweet_id} is already in list '{fav_list}'.")
            return False
        
        # Add tweet to list
        query = "INSERT INTO include (owner_id, lname, tid) VALUES (?, ?, ?)"
        if self.db.execute_query(query, (user_id, fav_list, tweet_id)):
            print(f"Tweet {tweet_id} added to list '{fav_list}'.")
            return True
        else:
            print("Failed to add tweet to list.")
            return False
