# Twitter-like Application User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Login and Registration](#login-and-registration)
4. [Main Features](#main-features)
   - [Viewing Timeline](#viewing-timeline)
   - [Searching for Tweets](#searching-for-tweets)
   - [Searching for Users](#searching-for-users)
   - [Composing Tweets](#composing-tweets)
   - [Managing Followers](#managing-followers)
   - [Favorite Lists](#favorite-lists)
5. [Navigation Tips](#navigation-tips)
6. [Troubleshooting](#troubleshooting)

## Introduction

This application is a command-line Twitter-like system that allows users to post tweets, follow other users, search for content, and manage favorite lists. The application uses a SQLite database to store user information, tweets, and relationships.

## Getting Started

### System Requirements

- Python 3.6 or higher
- SQLite3 database

### Running the Application

Launch the application by running:

```
python main.py <database_file>
```

Where `<database_file>` is the path to your SQLite database file. The database file will be provided at demo time, but you can use the sample database for testing.

Example:
```
python main.py data/sample.db
```

### Exiting the Application

You can exit the application at any time by:
- Selecting the "Exit" option from any menu
- Typing `!exit` at any prompt (except password entry)

## Login and Registration

### Login

1. From the main menu, select option `1. Login`
2. Enter your user ID
3. Enter your password (characters will not be displayed for security)
4. If credentials are correct, you'll be logged in and see the initial tweet feed

### Registration

1. From the main menu, select option `2. Sign up`
2. Enter your name
3. Enter your email (must contain @ and . characters)
4. Enter your phone number (digits only)
5. Enter a password
6. Upon successful registration, the system will provide you with a unique user ID
7. You'll be automatically logged in after registration

## Main Features

### Viewing Timeline

After login, the system automatically displays tweets and non-spam retweets from users you follow, ordered from newest to oldest. If there are more than 5 tweets, only 5 will be shown initially, and you can:

- Enter `n` to see the next page of tweets
- Enter `p` to see the previous page
- Enter `q` to quit viewing and proceed to the main menu
- Enter a tweet number to select and interact with that specific tweet

### Searching for Tweets

1. From the main menu, select option `1. Search for tweets`
2. Enter one or more keywords separated by commas
3. The system will display tweets that:
   - Contain any of the keywords in their text, or
   - Have hashtags matching any keyword with # prefix
4. Results are displayed in pages of 5 tweets
5. You can select a tweet by entering its number to:
   - View statistics (retweets and replies count)
   - Reply to the tweet
   - Retweet it
   - Add it to a favorite list

### Searching for Users

1. From the main menu, select option `2. Search for users`
2. Enter a keyword to search for users by name
3. The system will display users whose names contain the keyword
4. Results are sorted by name length (ascending) and displayed in pages of 5
5. You can select a user by entering their number to:
   - View their statistics (tweets, following, followers)
   - See their recent tweets
   - Follow them
   - View more of their tweets

### Composing Tweets

1. From the main menu, select option `3. Compose a tweet`
2. Enter your tweet text (maximum 280 characters)
3. Include hashtags by preceding words with # symbol (e.g., #hashtag)
4. The system will automatically extract hashtags and store them
5. Upon successful posting, the system will display the tweet ID

### Managing Followers

1. From the main menu, select option `4. List followers`
2. The system will display users who follow you in pages of 5
3. You can select a follower by entering their number to:
   - View their profile information
   - See their recent tweets
   - Follow them back
   - View more of their tweets

### Favorite Lists

1. From the main menu, select option `5. List favorite lists`
2. The system will display all your favorite lists and the tweets contained in each
3. When viewing tweet details (after searching), you can add tweets to favorite lists

## Navigation Tips

- Throughout the application, pagination works consistently:
  - `n`: Next page
  - `p`: Previous page
  - `q`: Quit/return to previous menu
  - Enter a number to select an item

- At any prompt (except password entry), typing `!exit` will exit the current operation and return to the main menu

- After completing operations, press Enter when prompted to continue

## Troubleshooting

### Common Issues

1. **Invalid credentials**: Ensure you're using the correct user ID and password for login

2. **Email format**: When registering, email must contain both @ and . characters

3. **Empty search results**: If search returns no results, try:
   - Using different keywords
   - Using fewer keywords
   - Checking case sensitivity (though searches are case-insensitive)

4. **Database connection errors**: Ensure the database file exists and is properly formatted

### Error Messages

- **"No database connection"**: The application couldn't connect to the database file
- **"Invalid credentials"**: The user ID and password combination is incorrect
- **"Email must contain '@' and '.'"**: Registration email format is invalid
- **"You have no followers"**: Displayed when trying to list followers but none exist
- **"You have no favorite lists"**: Displayed when trying to view favorite lists but none exist
