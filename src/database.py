"""
database.py - Database Module
Provides connection and query execution functionality for SQLite database operations.
"""
import sqlite3

class Database:
    """
    Database connection and operations handler.
    Manages SQLite database connections and provides methods for executing queries.
    """
    def __init__(self, db_file):
        """
        Initialize the database connection handler.
        
        Args:
            db_file (str): Path to the SQLite database file
        """
        self.conn = None
        self.db_file = db_file
        self.connect()

    def connect(self):
        """
        Create a connection to the SQLite database.
        Enables foreign key constraints for database integrity.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            # Enable foreign key constraints
            self.conn.execute("PRAGMA foreign_keys = ON;")
            print(f"Connected to database: {self.db_file}")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False

    def execute_query(self, query, params=None):
        """
        Execute an SQL query that modifies the database (INSERT, UPDATE, DELETE).
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            query (str): SQL query string
            params (tuple, optional): Parameters for the query
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.conn:
            print("No database connnection.")
            return False
        
        try:
            cursor = self.conn.cursor()
            # If parameters are given, execute query with parameters
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return False
    
    def execute_read_query(self, query, params=None):
        """
        Execute an SQL query that reads from the database (SELECT).
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            query (str): SQL query string
            params (tuple, optional): Parameters for the query
            
        Returns:
            list: Result of the query or None if error occurs
        """
        if not self.conn:
            print("No database connection.")
            return None
            
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"Error executing read query: {e}")
            return None
    
    def get_max_id(self, table, id_column):
        """
        Get the maximum ID value from a table.
        Used for generating new unique IDs.
        
        Args:
            table (str): Name of the table
            id_column (str): Name of the ID column
            
        Returns:
            int: Maximum ID value or 0 if table is empty
        """
        query = f"SELECT MAX(CAST({id_column} AS INTEGER)) FROM {table}"
        result = self.execute_read_query(query)
        
        # Check if result exists and is not None
        if result and result[0][0]:
            return int(result[0][0])
        return 0
    
    def close(self):
        """
        Close the database connection.
        Should be called when application exits to release resources.
        """
        if self.conn:
            try:
                self.conn.close()
                print("Database connection closed.")
            except sqlite3.Error as e:
                print(f"Error closing database connection: {e}")