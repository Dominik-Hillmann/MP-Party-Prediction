CREATE DATABASE IF NOT EXISTS mp_party_prediction;
USE mp_party_prediction;

-- Stores one user + meta info.
CREATE TABLE IF NOT EXISTS user(
    -- identification
    twitter_user_id         BIGINT NOT NULL, -- given by Twitter, not database
    screen_name             VARCHAR(250) NOT NULL, -- '@' handle
    -- interaction data
    favorites_count         INT NOT NULL, -- number of tweets this user has liked
    followers_count         INT NOT NULL, -- how many follow this account
    friends_count           INT NOT NULL, -- number this account is following
    listed_count            INT NOT NULL, -- contained in how many lists?
    statuses_count          INT NOT NULL, -- how many tweets, retweets?
    -- creation date of user
    creation_date           DATE NOT NULL,
    creation_time           TIME NOT NULL,
    -- further information that might become interesting
    loc                     VARCHAR(250) NOT NULL,
    link_color              VARCHAR(250) NOT NULL,
    sidebar_border_color    VARCHAR(250) NOT NULL,
    sidebar_fill_color      VARCHAR(250) NOT NULL,
    text_color              VARCHAR(250) NOT NULL,

    party                   VARCHAR(20) NOT NULL,

    PRIMARY KEY (twitter_user_id)
)

-- Stores one tweet + meta info.
CREATE TABLE IF NOT EXISTS tweet(
    -- identification of tweet and user who tweeted it
    twitter_tweet_id        BIGINT NOT NULL,
    twitter_user_id         BIGINT NOT NULL,
    -- tweet content
    full_text               VARCHAR(400) NOT NULL, -- not 280 because of converted Umlaute or similar
    favorites_count         INT NOT NULL,
    retweet_count           INT NOT NULL,
    -- meta information about tweet
    creation_date           DATE NOT NULL,
    creation_time           TIME NOT NULL,
    lang                    VARCHAR(5) NOT NULL,
    device                  VARCHAR(250) NOT NULL,
    uses_media              TINYINT(1) NOT NULL,

    PRIMARY KEY (twitter_tweet_id)
)

-- Stores all hashtags used in a tweet.
CREATE TABLE IF NOT EXISTS tweet_hashtag(
    twitter_tweet_id        BIGINT NOT NULL,
    hashtag_str             VARCHAR(100) NOT NULL
)

-- Stores all user mentioned in a certain tweet.
CREATE TABLE IF NOT EXISTS tweet_mentioned_user(
    twitter_tweet_id        BIGINT NOT NULL,
    mentioned_user_id       BIGINT NOT NULL -- id of user who issued this tweets can be seen by following this tweet_id
)
