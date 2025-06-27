import os
import praw
import tweepy
import random
import sys
from datetime import datetime, timezone

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)

consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api = tweepy.API(auth)

def is_good_post(post):
    return (
        20 < len(post.title) <= 280 and
        post.score >= 50 and
        not post.stickied and
        not post.over_18
    )

def tweet_showerthought():
    subreddit = reddit.subreddit('ShowerThoughts')
    posts = list(subreddit.hot(limit=200))
    good_posts = [p for p in posts if is_good_post(p)]
    if not good_posts:
        print("No good posts found.")
        return
    post = random.choice(good_posts)
    try:
        api.update_status(post.title)
        print(f"[{datetime.now(timezone.utc)}] Tweeted: {post.title[:60]}...")
    except Exception as e:
        print(f"Error tweeting: {e}")

if __name__ == "__main__":
    tweet_showerthought()

