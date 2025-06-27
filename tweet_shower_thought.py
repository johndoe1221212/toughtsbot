import praw
import tweepy
import random
import sys
from datetime import datetime, timezone

# Reddit credentials (hardcoded)
reddit = praw.Reddit(
    client_id='ezPbHCuMJj1ChN3AgnnNsQ',
    client_secret='Fo-_z2FPZU7cnkASLULylNDEJ0jCMQ',
    user_agent='ShowerThoughtsBot by u/Typical_Farm6742'
)

# Twitter credentials (hardcoded)
consumer_key = 'JYAsQiOuOQQavkxN4B1Uf1kch'
consumer_secret = '9kEoZ5UfxsDok8OP6QY9GdtxaoNEQPBTugcdMVP8yBtdNbE05Q'
access_token = '1938321275136442368-zGLGpqRpoU6yolyUMPXsVUZdMjwgXS'
access_token_secret = 'Pu0O9kSnDH6rPykLzzQ0eoIyDHAsnQePOtuzCJve8XLrN'

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


