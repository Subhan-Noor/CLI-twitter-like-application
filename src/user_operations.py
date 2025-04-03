""""
user_operations.py - User Operations Module
Provides functionality for user-related operations including searching, 
following, and retrieving user information.
"""
class UserOperations:
    """
    Handles all user-related operations in the Twitter-like application.
    Provides methods for searching users, managing followers, and retrieving user information.
    """
    
    def __init__(self, database, utils=None):
        """
        Initialize the user operations handler.
        
        Args:
            database: Database object for executing queries
            utils: Utils object for common utility functions
        """
        self.db = database
        self.utils = utils
    
    def search_users(self, keyword, offset=0, limit=5):
        """
        Search for users by name (case-insensitive).
        Results are ordered by name length (ascending).
        
        Args:
            keyword (str): Keyword to search for in user names
            offset (int): Offset for pagination
            limit (int): Limit for pagination
            
        Returns:
            list: List of matching users [(user_id, name), ...]
        """
        query = """
        SELECT usr, name 
        FROM users 
        WHERE LOWER(name) LIKE LOWER(?) 
        ORDER BY LENGTH(name) ASC
        LIMIT ? OFFSET ?
        """
        
        params = (f"%{keyword}%", limit, offset)
        return self.db.execute_read_query(query, params)
    
    def list_followers(self, user_id, offset=0, limit=5):
        """
        List all followers of the current user with pagination.
        
        Args:
            user_id (str): ID of the user
            offset (int): Offset for pagination
            limit (int): Limit for pagination
            
        Returns:
            list: List of followers [(follower_id, name), ...]
        """
        query = """
        SELECT u.usr, u.name
        FROM follows f
        JOIN users u ON f.flwer = u.usr
        WHERE f.flwee = ?
        ORDER BY u.name
        LIMIT ? OFFSET ?
        """
        
        return self.db.execute_read_query(query, (user_id, limit, offset))

    def display_user_search_results(self, users):
        """
        Display user search results with formatting.
        
        Args:
            users: List of user data tuples [(id, name), ...]
            
        Returns:
            bool: True if users were displayed, False otherwise
        """
        if not users:
            # Message will be displayed by the calling function based on offset
            return False
        
        print("\n=== User Search Results ===")
        for i, user in enumerate(users, 1):
            print(f"{i}. User ID: {user[0]}, Name: {user[1]}")

        return True

    def get_user_stats(self, user_id):
        """
        Get statistics about a user including tweet count, followers, and following.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            dict: Dictionary with user statistics
        """
        tweet_query = "SELECT COUNT(*) FROM tweets WHERE writer_id = ?"
        tweet_result = self.db.execute_read_query(tweet_query, (user_id,))
        
        # Get following count
        following_query = "SELECT COUNT(*) FROM follows WHERE flwer = ?"
        following_result = self.db.execute_read_query(following_query, (user_id,))
        
        # Get follower count
        follower_query = "SELECT COUNT(*) FROM follows WHERE flwee = ?"
        follower_result = self.db.execute_read_query(follower_query, (user_id,))

        return{
            "tweet_count": tweet_result[0][0] if tweet_result else 0,
            "following_count": following_result[0][0] if following_result else 0,
            "follower_count": follower_result[0][0] if follower_result else 0
        }

    def get_recent_tweets(self, user_id, limit=3):
        """
        Get the most recent tweets and retweets from a user.
        
        Args:
            user_id (str): ID of the user
            limit (int, optional): Maximum number of tweets to retrieve
            
        Returns:
            list: List of recent tweets and retweets in format [tid, text, date, time, type]
                where type is 'tweet' or 'retweet'
        """
        # Query for original tweets by the user
        tweets_query = """
        SELECT 
            tid, 
            text, 
            tdate, 
            ttime,
            'tweet' AS type
        FROM tweets
        WHERE writer_id = ?
        """
        
        # Query for retweets by the user
        retweets_query = """
        SELECT 
            t.tid, 
            t.text, 
            r.rdate AS tdate, 
            t.ttime,
            'retweet' AS type
        FROM retweets r
        JOIN tweets t ON r.tid = t.tid
        WHERE r.retweeter_id = ? AND r.spam = 0
        """
        
        # Combine and sort by date, then time
        query = f"""
        SELECT * FROM (
            {tweets_query}
            UNION ALL
            {retweets_query}
        )
        ORDER BY tdate DESC, ttime DESC
        LIMIT ?
        """

        return self.db.execute_read_query(query, (user_id, user_id, limit))
    
    def display_user_details(self, user_id, name=None):
        """
        Display detailed information about a user.
        Shows user's name, stats, and recent tweets.
        
        Args:
            user_id (str): ID of the user
            name (str, optional): Name of the user (if already known)
        """
        # Fetch name if not provided
        if not name:
            name_query = "SELECT name FROM users WHERE usr = ?"
            name_result = self.db.execute_read_query(name_query, (user_id,))
            if name_result:
                name = name_result[0][0]
            else:
                name = "Unknown"

        # Get user statistics
        stats = self.get_user_stats(user_id)

        # Get recent tweets
        recent_tweets = self.get_recent_tweets(user_id)

        # Display user profile
        print(f"\n=== User Details: {name} (ID: {user_id}) ===")
        print(f"Tweets: {stats['tweet_count']}")
        print(f"Following: {stats['following_count']}")
        print(f"Followers: {stats['follower_count']}")

        # Display recent tweets
        if recent_tweets:
            print("\nRecent Tweets:")
            for i, tweet in enumerate(recent_tweets, 1):
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
            print("\nNo recent tweets.")

    def follow_user(self, follower_id, followee_id):
        """
        Make the current user follow another user.
        
        Args:
            follower_id (str): ID of the user who wants to follow
            followee_id (str): ID of the user to be followed
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if user is trying to follow themselves
        if follower_id == followee_id:
            print("You cannot follow yourself.")
            return False
            
        # Check if already following
        check_query = "SELECT COUNT(*) FROM follows WHERE flwer = ? AND flwee = ?"
        check_result = self.db.execute_read_query(check_query, (follower_id, followee_id))

        if check_result and check_result[0][0] > 0:
            print("You are already following this user.")
            return False
        
        current_date = self.utils.get_formatted_date()

        follow_query = "INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, ?)"
        return self.db.execute_query(follow_query, (follower_id, followee_id, current_date))
    
    def display_followers(self, followers):
        """
        Display followers with formatting.
        
        Args:
            followers: List of follower data tuples [(id, name), ...]
            
        Returns:
            bool: True if followers were displayed, False otherwise
        """
        if not followers:
            # Message will be displayed by the calling function based on offset
            return False
        
        print("\n=== Your Followers ===")
        for i, follower in enumerate(followers, 1):
            print(f"{i}. User ID: {follower[0]}, Name: {follower[1]}")

        return True