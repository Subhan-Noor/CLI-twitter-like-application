# Database Schema Documentation

## Overview

This document outlines the database schema. The database uses SQLite and consists of several tables designed to store user information, tweets, retweets, hashtag mentions, follows relationships, and favorite lists.

## Tables

### users

Stores information about registered users.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| usr | TEXT | Unique user identifier | PRIMARY KEY |
| name | TEXT | User's full name | NOT NULL |
| email | TEXT | User's email address | NOT NULL, must contain '@' and '.' |
| phone | TEXT | User's phone number | NOT NULL |
| pwd | TEXT | User's password | NOT NULL |

### follows

Records following relationships between users.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| flwer | TEXT | ID of the follower | FOREIGN KEY → users(usr) |
| flwee | TEXT | ID of the followee | FOREIGN KEY → users(usr) |
| start_date | TEXT | Date when follow started | Format: YYYY-MM-DD |

Primary Key: (flwer, flwee)

### tweets

Stores all tweets posted by users.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| tid | INTEGER | Unique tweet identifier | PRIMARY KEY |
| writer_id | TEXT | ID of the user who wrote the tweet | FOREIGN KEY → users(usr) |
| text | TEXT | Content of the tweet | NOT NULL |
| tdate | TEXT | Date the tweet was posted | Format: YYYY-MM-DD |
| ttime | TEXT | Time the tweet was posted | Format: HH:MM:SS |
| replyto_tid | INTEGER | ID of the tweet this is replying to | FOREIGN KEY → tweets(tid), NULL for non-replies |

### retweets

Records information about retweets.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| tid | INTEGER | ID of the original tweet | FOREIGN KEY → tweets(tid) |
| retweeter_id | TEXT | ID of the user who retweeted | FOREIGN KEY → users(usr) |
| writer_id | TEXT | ID of the original tweet writer | FOREIGN KEY → users(usr) |
| spam | INTEGER | Flag indicating if retweet is spam | 0 = Not spam, 1 = Spam |
| rdate | TEXT | Date the retweet was made | Format: YYYY-MM-DD |

Primary Key: (tid, retweeter_id)

### hashtag_mentions

Maps tweets to their hashtags.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| tid | INTEGER | ID of the tweet | FOREIGN KEY → tweets(tid) |
| term | TEXT | Hashtag term | Format: #word (includes # symbol) |

Primary Key: (tid, term)

### lists

Stores information about user's favorite lists.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| owner_id | TEXT | ID of the list owner | FOREIGN KEY → users(usr) |
| lname | TEXT | Name of the list | NOT NULL |

Primary Key: (owner_id, lname)

### include

Records which tweets are included in which favorite lists.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| owner_id | TEXT | ID of the list owner | FOREIGN KEY → users(usr) |
| lname | TEXT | Name of the list | FOREIGN KEY → lists(lname) |
| tid | INTEGER | ID of the included tweet | FOREIGN KEY → tweets(tid) |

Primary Key: (owner_id, lname, tid)

## Foreign Key Relationships

- `follows.flwer` → `users.usr`
- `follows.flwee` → `users.usr`
- `tweets.writer_id` → `users.usr`
- `tweets.replyto_tid` → `tweets.tid`
- `retweets.tid` → `tweets.tid`
- `retweets.retweeter_id` → `users.usr`
- `retweets.writer_id` → `users.usr`
- `hashtag_mentions.tid` → `tweets.tid`
- `lists.owner_id` → `users.usr`
- `include.owner_id` → `users.usr`
- `include.lname` → refers to `lists.lname` with the same `owner_id`
- `include.tid` → `tweets.tid`

## Notes

- Foreign key constraints must be enabled for each session in SQLite3 with:
  ```sql
  PRAGMA foreign_keys = ON;
  ```
- All date fields follow the YYYY-MM-DD format
- All time fields follow the HH:MM:SS format
- The application handles case sensitivity - string matches (except passwords) are case-insensitive
- Hashtags in the `hashtag_mentions` table include the '#' symbol
