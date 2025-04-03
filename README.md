# CLI Twitter-like Application

## Project Overview

This project implements a command-line Twitter-like application for CMPUT 291 (Winter 2025). The system allows users to register, login, post tweets, follow other users, search for content, and manage favorite lists.

## Features

- User authentication (login and registration)
- Tweet composition with hashtag support
- Tweet searching by keywords or hashtags
- User searching by name
- Following/follower management
- Favorite lists for tweet organization
- Replying to and retweeting tweets
- Pagination for all list displays

## Project Structure

```
twitter-app/
├── src/              # Source code directory
├── data/             # Sample database for testing
├── docs/             # Documentation
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Setup and Installation

1. Ensure you have Python 3.6+ installed
2. No additional packages are required beyond the Python standard library
3. Clone this repository

## Running the Application

```bash
python src/main.py <database_file>
```

Where `<database_file>` is the path to the SQLite database file.

## Implementation Notes

- All string matching except passwords is case-insensitive
- SQL injection protection implemented using parameterized queries
- Foreign key constraints are enabled for database integrity
- Error handling provides user-friendly messages
- Pagination used for all list displays to handle large data sets

## Acknowledgments

This project makes use of concepts and code patterns from the following sources:
1. **Custom Exception Implementation** GeeksforGeeks - "Define Custom Exceptions in Python" URL: https://www.geeksforgeeks.org/define-custom-exceptions-in-python/ Date accessed: March 16, 2025
2. **Exception-based Control Flow** Reddit r/pythontips - "Don't use sys.exit(1), raise an exception or assert instead!" URL: https://www.reddit.com/r/pythontips/comments/d0aysf/dont_use_sysexit1_raise_an_exception_or_assert/ Date accessed: March 16, 2025
