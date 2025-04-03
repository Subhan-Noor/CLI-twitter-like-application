"""
main.py - Entry Point Module
Main application module.
Handles application flow, command-line parsing, and menu interactions.
"""
import sys
from database import Database
from auth import Auth
from tweet_operations import TweetOperations
from user_operations import UserOperations
from list_operations import ListOperations
from utils import Utils, ExitRequestException


class TwitterApp:
    """
    Main application class for the Twitter-like system.
    Manages application flow, user sessions, and component interactions.
    """

    def __init__(self, db_file):
        """
        Initialize the application with database connection and component classes.
        
        Args:
            db_file (str): Path to the SQLite database file
        """
        # Component classes
        self.db = Database(db_file)
        self.utils = Utils()
        self.auth = Auth(self.db, self.utils)
        self.tweet_ops = TweetOperations(self.db, self.utils)
        self.user_ops = UserOperations(self.db, self.utils)
        self.list_ops = ListOperations(self.db, self.utils)

        # Application state
        self.current_user_id = None
        self.exit_requested = False

    def display_main_menu(self):
        """
        Display the main menu options for login/signup.
        Entry point menu before user authentication.
        """
        self.utils.display_menu("Twitter", [
            "Login",
            "Sign up",
            "Exit"
        ])

    def process_main_menu_choice(self):
        """
        Process user selection from main menu.
        Handles login, registration, or exit options.
        
        Returns:
            bool: True if user is logged in, False otherwise
        """
        try:
            choice = self.utils.safe_input("\nEnter your choice (1-3): ")
            if choice == '1':
                self.current_user_id = self.auth.login()
                return bool(self.current_user_id)
            
            elif choice == '2':
                self.current_user_id = self.auth.register()
                return bool(self.current_user_id)
            
            elif choice == '3':
                print("\nExiting program...")
                self.exit_requested = True
                return False
            
            else:
                print("\nInvalid choice. Please try again.")
                self.utils.wait_for_user()
                return False
        except ExitRequestException:
            self.exit_requested = True
        
    def display_logged_in_menu(self):
        """
        Display menu options for logged-in users.
        Shows all available actions for an authenticated user.
        """
        self.utils.display_menu(f"Main Menu (User: {self.current_user_id})", [
            "Search for tweets",
            "Search for users",
            "Compose a tweet",
            "List followers",
            "List favorite lists",
            "Logout",
            "Exit"
        ])

    def search_tweets_menu(self):
        """
        Handle tweet search functionality.
        Allows users to search tweets by keywords or hashtags and interact with results.
        """
        try:
            print("\n=== Search Tweets ===")
            keywords = self.utils.safe_input("Enter one or more keywords (comma-separated): ")

            def search_with_keywords(offset, limit):
                return self.tweet_ops.search_tweets(keywords, offset, limit)

            selected_tweet, action = self.utils.handle_pagination(
                get_data_func=search_with_keywords,
                display_func=self.tweet_ops.display_tweet_search_results,
                empty_message="No matching tweets found.",
                no_more_message="No more tweets to display.",
                prompt="View more tweets? (n: next, p: previous, q: quit, or enter tweet number): "
            )

            if action == 'select' and selected_tweet:
                self.tweet_details_menu(selected_tweet)
        except ExitRequestException:
            self.exit_requested = True
        
    def tweet_details_menu(self, tweet):
        """
        Show tweet details and interaction options.
        Allows replying, retweeting, and adding to favorites.

        Args:
            tweet: Tweet data tuple
        """
        try:
            tid = tweet[1]

            # Display tweet statistics
            self.tweet_ops.display_tweet_statistics(tid)

            self.utils.display_menu(f"Options for Tweet {tid}", [
                "Reply to this tweet",
                "Retweet",
                "Add to favorite list",
                "Return to previous menu"
            ])

            choice = self.utils.get_valid_input(1, 4)

            if choice == 1:
                reply_text = self.utils.safe_input("Enter your reply: ")
                new_tid = self.tweet_ops.compose_tweet(self.current_user_id, reply_text, tid)
                if new_tid:
                    print(f"Reply posted with ID: {new_tid}")
                self.utils.wait_for_user()

            elif choice == 2:
                if self.tweet_ops.retweet(self.current_user_id, tid):
                    print("Tweet has been retweeted successfully.")
                else:
                    print("Failed to retweet.")
                self.utils.wait_for_user()

            elif choice == 3:
                # Implement add to favorite list
                if self.list_ops.add_tweet_to_list(self.current_user_id, None, tid):
                    pass  # Message is already printed in add_tweet_to_list
                self.utils.wait_for_user()
        except ExitRequestException:
            self.exit_requested = True

    def compose_tweet_menu(self):
        """
        Handle tweet composition.
        Allows users to create new tweets with optional hashtags.
        """
        try:
            text = self.utils.safe_input("Enter your tweet: ")

            new_tid = self.tweet_ops.compose_tweet(self.current_user_id, text)
            if new_tid:
                print(f"Tweet posted successfully with ID: {new_tid}")
            else:
                print("Failed to post tweet.")

            self.utils.wait_for_user()
        except ExitRequestException:
            self.exit_requested = True

    def search_users_menu(self):
        """
        Handle user search functionality.
        Allows searching for users by name and interacting with results.
        """
        try:
            keyword = self.utils.safe_input("Enter a keyword to search for users: ")

            def search_with_keyword(offset, limit):
                return self.user_ops.search_users(keyword, offset, limit)
            
            selected_user, action = self.utils.handle_pagination(
                get_data_func=search_with_keyword,
                display_func=self.user_ops.display_user_search_results,
                empty_message="No matching users found.",
                no_more_message="No more users to display.",
                prompt="View more users? (n: next, p: previous, q: quit, or enter user number): "
            )
            
            if action == 'select' and selected_user:
                self.user_details_menu(selected_user)
        except ExitRequestException:
            self.exit_requested = True

    def user_details_menu(self, user):
        """
        Show user details and interaction options.
        Displays user statistics and allows following/viewing tweets.
        
        Args:
            user: User data tuple (user_id, name)
        """
        try:
            user_id, name = user
            
            # Display user details
            self.user_ops.display_user_details(user_id, name)
            
            self.utils.display_menu("Options", [
                "Follow this user",
                "See more tweets",
                "Return to previous menu"
            ])
            
            choice = self.utils.get_valid_input(1, 3)
            
            if choice == 1:
                if self.user_ops.follow_user(self.current_user_id, user_id):
                    print(f"You are now following {name}.")
                    self.utils.wait_for_user()  # Wait for user to acknowledge
                else:
                    print("Failed to follow user.")
                    self.utils.wait_for_user()  # Wait for user to acknowledge
            
            elif choice == 2:
                more_tweets = self.user_ops.get_recent_tweets(user_id, 10)  # Get more tweets
                if more_tweets:
                    print("\n=== More Tweets ===")
                    for i, tweet in enumerate(more_tweets, 1):
                        tid = tweet[0]
                        text = tweet[1]
                        date = tweet[2]
                        time = tweet[3]
                        tweet_type = tweet[4] if len(tweet) > 4 else "tweet"  # Default to "tweet" if type not specified
                        
                        print(f"{i}. Type: {tweet_type}, TID: {tid}, Date: {date}, Time: {time}")
                        print(f"   Text: {text}")
                        print(f"   Spam: No")
                        print("-" * 50)
                else:
                    print("\nNo more tweets to display.")
                self.utils.wait_for_user()
        except ExitRequestException:
            self.exit_requested = True

    def list_followers_menu(self):
        """
        Handle followers listing with pagination.
        Shows all users following the current user.
        """
        try:
            selected_follower, action = self.utils.handle_pagination(
                get_data_func=self.user_ops.list_followers,
                display_func=self.user_ops.display_followers,
                id_param=self.current_user_id,
                empty_message="You have no followers.",
                no_more_message="No more followers to display.",
                prompt="View more followers? (n: next, p: previous, q: quit, or enter follower number): "
            )
            
            if action == 'select' and selected_follower:
                self.user_details_menu(selected_follower)
        except ExitRequestException:
            self.exit_requested = True

    def list_favorite_lists_menu(self):
        """
        Handle favorite lists display.
        Shows all favorite lists and their contents for the current user.
        """
        self.list_ops.display_favorite_lists(self.current_user_id)
        self.utils.wait_for_user()

    def process_logged_in_choice(self): 
        """
        Process user selection when logged in.
        Handles various actions available to authenticated users.
        
        Returns:
            bool: True if user should stay logged in, False otherwise
        """
        try:
            choice = self.utils.safe_input("\nEnter your choice (1-7): ")
            
            if choice == '1':
                # Search for tweets
                self.search_tweets_menu()
                return True
            
            elif choice == '2':
                # Search for users
                print("\n=== Search Users ===")
                self.search_users_menu()
                return True
            
            elif choice == '3':
                # Compose a tweet
                print("\n=== Compose Tweet ===")
                self.compose_tweet_menu()
                return True
            
            elif choice == '4':
                # List followers
                self.list_followers_menu()
                return True
            
            elif choice == '5':
                # List favorite lists
                self.list_favorite_lists_menu()
                return True
            
            elif choice == '6':
                print("\nLogging out...")
                self.current_user_id = None
                return False
            
            elif choice == '7':
                print("\nExiting program...")
                self.exit_requested = True
                return False
            
            else:
                print("\nInvalid choice. Please try again.")
                self.utils.wait_for_user()
                return True
        except ExitRequestException:
            self.exit_requested = True

    def show_followed_tweets(self):
        """
        Show tweets from followed users with pagination.
        Displays on login and allows interaction with tweets.
        """
        try:
            selected_tweet, action = self.utils.handle_pagination(
                get_data_func=self.tweet_ops.get_initial_tweet_feed,
                display_func=self.tweet_ops.display_tweets,
                id_param=self.current_user_id,
                empty_message="No tweets from users you follow.",
                no_more_message="No more tweets to display.",
                prompt="View more tweets? (n: next, p: previous, q: quit, or enter tweet number): "
            )

            if action == 'select' and selected_tweet:
                self.tweet_details_menu(selected_tweet)
        except ExitRequestException:
            self.exit_requested = True

    def run(self):
        """
        Run the main application loop.
        Handles the overall flow of the application.
        """
        try:
            while not self.exit_requested:
                self.utils.clear_screen()
                self.display_main_menu()
                logged_in = self.process_main_menu_choice()

                if logged_in and self.current_user_id:
                    # Show intitial tweet feed
                    self.show_followed_tweets()

                    # Enter logged-in menu loop
                    stay_logged_in = True
                    while stay_logged_in and not self.exit_requested:
                        self.utils.clear_screen()
                        self.display_logged_in_menu()
                        stay_logged_in = self.process_logged_in_choice()

        finally:
            # Ensure connection close even if error occurs
            self.db.close()


def main():
    """
    Program entry point.
    Handles command line arguments and initializes the application.
    """
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <database_file>")
        sys.exit(1)

    db_file = sys.argv[1]
    app = TwitterApp(db_file)

    Utils.clear_screen()

    print("\nWelcome to 'Twitter'")
    print(f"Type '{Utils.EXIT_KEYWORD}' at any prompt (but passwords) to exit the application")
    input("Press enter to continue...")

    app.run()

if __name__ == '__main__':
    main()
