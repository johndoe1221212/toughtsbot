import os
import praw
import tweepy
import random
import time
from datetime import datetime, timedelta
import threading

# Reddit credentials (from GitHub Secrets)
reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    user_agent=os.environ['REDDIT_USER_AGENT']
)

# Twitter credentials (from GitHub Secrets)
client = tweepy.Client(
    bearer_token=os.environ['TWITTER_BEARER_TOKEN'],
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
)

def is_good_post(post):
    return (
        20 < len(post.title) <= 280 and
        post.score >= 50 and
        not post.stickied and
        not post.over_18
    )

def fetch_good_posts():
    subreddit = reddit.subreddit('ShowerThoughts')
    posts = list(subreddit.hot(limit=100))
    candidates = [p for p in posts if is_good_post(p)]
    return candidates

def post_thought(thought):
    try:
        response = client.create_tweet(text=thought)
        print(f"[{datetime.utcnow()}] Tweeted: {thought[:60]}...")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Error tweeting: {e}")

def main():
    posts = fetch_good_posts()
    if not posts:
        print("No good posts found.")
        return

    # Tweet 1 post per run
    post = random.choice(posts)
    post_thought(post.title)

if __name__ == "__main__":
    main()

