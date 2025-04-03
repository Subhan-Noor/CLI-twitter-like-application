"""
tweet_operations.py - Tweet Operations Module
Provides functionality for tweet-related operations including searching, 
composition, retrieval, and statistics.
"""

# import sqlite3
import re
from datetime import datetime


class TweetOperations:
    """
    Handles all tweet-related operations in the Twitter-like application.
    Provides methods for searching, composing, and managing tweets.
    """
    def __init__(self, database, utils=None):
        """
        Initialize the tweet operations handler.
        
        Args:
            database: Database object for executing queries
            utils: Utils object for common utility functions
        """
        self.db = database
        self.utils = utils

    def search_tweets(self, keywords, offset=0, limit=5):
        """
        Search for tweets matching keywords or hashtags.
        
        Args:
            keywords (str): Comma-separated keywords to search for
            offset (int): Offset for pagination
            limit (int): Limit for pagination
            
        Returns:
            list: List of matching tweets ordered by date (newest first)
        """
        keyword_list = [k.strip() for k in keywords.split(',')]
        all_results = []

        for word in keyword_list:
            if word == '':
                continue

            # Search for hashtags with # prefix
            if word.startswith('#'):
                query_hashtag = """
                SELECT
                    'tweet' AS type,
                    t.tid,
                    t.tdate,
                    t.ttime,
                    t.text,
                    0 AS spam
                FROM tweets AS t
                JOIN hashtag_mentions AS ht ON ht.tid = t.tid
                WHERE LOWER(ht.term) = LOWER(?)
                ORDER BY t.tdate DESC, t.ttime DESC
                """
                results = self.db.execute_read_query(query_hashtag, (word,))
                if results:
                    all_results.extend(results)

            # Search for keywords in tweet text or matching hashtags without # prefix
            else:
                # Search in tweet text
                query_text = """
                SELECT
                    'tweet' AS type,
                    tid,
                    tdate,
                    ttime,
                    text,
                    0 AS spam
                FROM tweets
                WHERE LOWER(text) LIKE LOWER(?)
                ORDER BY tdate DESC, ttime DESC
                """
                results = self.db.execute_read_query(query_text, (f'%{word}%',))
                if results:
                    all_results.extend(results)

                # Search in hashtags without # prefix
                query_hashtag_without_prefix = """
                SELECT
                    'tweet' AS type,
                    t.tid,
                    t.tdate,
                    t.ttime,
                    t.text,
                    0 AS spam
                FROM tweets AS t
                JOIN hashtag_mentions AS ht ON ht.tid = t.tid
                WHERE LOWER(ht.term) = LOWER(?)
                ORDER BY t.tdate DESC, t.ttime DESC
                """
                results = self.db.execute_read_query(query_hashtag_without_prefix, (word,))
                if results:
                    all_results.extend(results)

        # Remove duplicate tweets
        unique_results = []
        seen_tids = set()

        for tweet in all_results:
            if tweet[1] not in seen_tids:
                unique_results.append(tweet)
                seen_tids.add(tweet[1])

        # Handle sorting with potential None values
        def safe_sort_key(tweet):
            date = tweet[2] if tweet[2] is not None else ""
            time = tweet[3] if tweet[3] is not None else ""
            return (date, time)
        
        unique_results.sort(key=safe_sort_key, reverse=True)

        # Apply pagination
        return unique_results[offset:offset+limit]

    def display_tweet_search_results(self, tweets):
        """
        Display search results with formatted output.
        
        Args:
            tweets: List of tweet data to display
            
        Returns:
            bool: True if tweets were displayed, False otherwise
        """
        if not tweets:
            # Message will be displayed by the calling function based on offset
            return False
        
        print("\n=== Search Results ===")
        for i, tweet in enumerate(tweets, 1):
            print(f"{i}. Type: {tweet[0]}, TID: {tweet[1]}, Date: {tweet[2]}, Time: {tweet[3]}")
            print(f"\tText: {tweet[4]}")
            print(f"\tSpam: {'Yes' if tweet[5] == 1 else 'No'}")
            print("-" * 50)

        return True

    def get_tweet_statistics(self, tweet_id):
        """
        Get statistics about a tweet including retweet and reply counts.
        
        Args:
            tweet_id (str): ID of the tweet
            
        Returns:
            dict: Dictionary with tweet statistics
        """
        # Count non-spam retweets
        retweet_query = "SELECT COUNT(*) FROM retweets WHERE tid = ? AND spam = 0"
        retweet_result = self.db.execute_read_query(retweet_query, (tweet_id,))

        # Count replies to this tweet
        reply_query = "SELECT COUNT(*) FROM tweets WHERE replyto_tid = ?"
        reply_result = self.db.execute_read_query(reply_query, (tweet_id,))

        return {
            "retweet_count": retweet_result[0][0] if retweet_result else 0,
            "reply_count": reply_result[0][0] if reply_query else 0
        }

    def display_tweet_statistics(self, tweet_id):
        """
        Display formatted statistics for a tweet.
        
        Args:
            tweet_id (str): ID of the tweet
        """
        stats = self.get_tweet_statistics(tweet_id)

        print(f"\n=== Statistics for Tweet {tweet_id} ===")
        print(f"Retweets: {stats['retweet_count']}")
        print(f"Replies: {stats['reply_count']}")

    def extract_hashtags(self, tweet_text):
        """
        Extract unique hashtags from tweet text.
        
        Args:
            tweet_text (str): Text of the tweet
            
        Returns:
            list: List of unique hashtags (including the # symbol)
        """
        # Find all hashtags (words that start with #)
        hashtags = re.findall(r'(#\w+)', tweet_text)

        # Return list of unique hashtags
        return list(set(hashtags))
    
    def validate_tweet_text(self, text):
        """
        Validate tweet text against length constraints.
        
        Args:
            text (str): Text of the tweet
            
        Returns:
            tuple: (bool, str) indicating validity and error message if invalid
        """
        MIN_LENGTH = 1
        MAX_LENGTH = 280 # Standard max length on twitter

        if not text or len(text.strip()) < MIN_LENGTH:
            return False, "Tweet cannot be empty"
        
        if len(text) > MAX_LENGTH:
            return False, f"Tweet exceeds maximum length of {MAX_LENGTH}"
        
        return True, ""

    def compose_tweet(self, user_id, text, reply_to=None):
        """
        Create a new tweet and store it in the database.
        Also extracts and stores hashtags.
        
        Args:
            user_id (str): ID of the user composing the tweet
            text (str): Text of the tweet
            reply_to (str, optional): ID of the tweet being replied to
            
        Returns:
            str: ID of the new tweet if successful, None otherwise
        """
        # Validate tweet text
        is_valid, error_message = self.validate_tweet_text(text)
        if not is_valid:
            print(error_message)
            return None

        # Get current date and time
        current_date = self.utils.get_formatted_date()
        current_time = self.utils.get_formatted_time()

        # Generate new tweet ID
        max_tid_query = "SELECT MAX(tid) FROM tweets"
        max_tid_result = self.db.execute_read_query(max_tid_query)
        new_tid = 1
        if max_tid_result and max_tid_result[0][0]:
            new_tid = max_tid_result[0][0] + 1

        # Insert the tweet
        tweet_query = """
        INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        tweet_params = (new_tid, user_id, text, current_date, current_time, reply_to)

        if not self.db.execute_query(tweet_query, tweet_params):
            return None
        
        # Extract and store hashtags
        hashtags = self.extract_hashtags(text)

        for hashtag in hashtags:
            hashtag_query = "INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?)"
            self.db.execute_query(hashtag_query, (new_tid, hashtag))

        return str(new_tid)

    def retweet(self, user_id, tweet_id):
        """
        Create a retweet of an existing tweet.
        
        Args:
            user_id (str): ID of the retweeting user
            tweet_id (str): ID of the tweet to retweet
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the writer_id of the original tweet
            query_writer = "SELECT writer_id FROM tweets WHERE tid = ?"
            writer_result = self.db.execute_read_query(query_writer, (tweet_id,))
            
            if not writer_result:
                print('No tweet with the given tweet id. Retweet not created.')
                return False
                
            writer_id = writer_result[0][0]
            
            # Check if already retweeted
            check_query = """
            SELECT COUNT(*) FROM retweets 
            WHERE tid = ? AND retweeter_id = ?
            """
            check_result = self.db.execute_read_query(check_query, (tweet_id, user_id))
            
            if check_result and check_result[0][0] > 0:
                print('You have already retweeted this tweet.')
                return False
            
            # Set retweet parameters
            spam = 0
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Insert retweet
            query_retweet = """
            INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate)
            VALUES (?, ?, ?, ?, ?)
            """
            if self.db.execute_query(query_retweet, (tweet_id, user_id, writer_id, spam, current_date)):
                print('Retweet created successfully.')
                return True
            else:
                print('Failed to create retweet.')
                return False
                
        except Exception as e:
            print(f"Error creating retweet: {e}")
            return False
        
    def display_tweets(self, tweets, start_idx=0):
        """
        Display tweets with formatted output.
        
        Args:
            tweets: List of tweet data to display
            start_idx (int): Starting index for display
            
        Returns:
            bool: True if tweets were displayed, False otherwise
        """
        if not tweets:
            # Message will be displayed by the calling function based on context
            return False
        
        print("\n=== Tweets ===")
        for i, tweet in enumerate(tweets, 1):
            print(f"{i}. Type: {tweet[0]}, TID: {tweet[1]}, Date: {tweet[2]}, Time: {tweet[3]}")
            print(f"   Text: {tweet[4]}")
            print(f"   Spam: {'Yes' if tweet[5] == 1 else 'No'}")
            print("-" * 50)
        
        return True
    
    def get_initial_tweet_feed(self, user_id, offset=0, limit=5):
        """
        Get tweets and non-spam retweets from users followed by the current user.
        Results are ordered from newest to oldest.
        
        Args:
            user_id (str): Current user ID
            offset (int): Offset for pagination
            limit (int): Limit for pagination
            
        Returns:
            list: List of tweets/retweets from followed users
        """
        query_tweets = """
        SELECT 
            'tweet' AS type,  -- Column 1: type
            t.tid,            -- Column 2: tid
            t.tdate,          -- Column 3: date
            t.ttime,          -- Column 4: time
            t.text,           -- Column 5: text
            0 AS spam         -- Column 6: spam flag
        FROM tweets t
        JOIN follows f ON t.writer_id = f.flwee
        WHERE f.flwer = ?
        """
        
        # Query for retweets from followed users
        query_retweets = """
        SELECT 
            'retweet' AS type,  -- Column 1: type 
            t.tid,              -- Column 2: tid
            t.tdate,            -- Column 3: date
            t.ttime,            -- Column 4: time
            t.text,             -- Column 5: text
            r.spam              -- Column 6: spam flag
        FROM retweets r
        JOIN tweets t ON r.tid = t.tid
        JOIN follows f ON r.retweeter_id = f.flwee
        WHERE f.flwer = ? AND r.spam = 0
        """
        
        # Combine using UNION ALL, then sort and paginate
        query = f"""
        SELECT * FROM (
            {query_tweets}
            UNION ALL
            {query_retweets}
        ) 
        ORDER BY tdate DESC, ttime DESC
        LIMIT ? OFFSET ?
        """
        
        return self.db.execute_read_query(query, (user_id, user_id, limit, offset))
