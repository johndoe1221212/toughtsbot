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
    posts = list(subreddit.hot(limit=200))  # more posts to choose from
    candidates = [p for p in posts if is_good_post(p)]
    return candidates

def post_thought(thought):
    try:
        response = client.create_tweet(text=thought)
        print(f"[{datetime.utcnow()} UTC] Tweeted: {thought[:60]}... (ID: {response.data['id']})")
    except Exception as e:
        print(f"[{datetime.utcnow()} UTC] Error tweeting: {e}")

def schedule_posts(posts):
    """
    Schedule 16 posts daily at chosen best UTC hours with ±3 min randomness.
    """
    best_hours_utc = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 23]  # 16 hours
    posted_indices = set()

    def schedule_single_post(post_index, scheduled_time):
        now = datetime.utcnow()
        wait_seconds = (scheduled_time - now).total_seconds()
        if wait_seconds < 0:
            wait_seconds += 86400  # schedule for next day if time already passed

        threading.Timer(wait_seconds, lambda: post_thought(posts[post_index].title)).start()
        print(f"Scheduled post #{post_index} at {scheduled_time.strftime('%H:%M:%S')} UTC in {int(wait_seconds)} seconds.")

    for i in range(min(16, len(posts))):
        base_hour = best_hours_utc[i]
        # Add random offset between -3 and +3 minutes
        minute_offset = random.randint(-3, 3)
        scheduled_time = datetime.utcnow().replace(hour=base_hour, minute=0, second=0, microsecond=0) + timedelta(minutes=minute_offset)

        # Pick a unique post index randomly
        available_indices = set(range(len(posts))) - posted_indices
        if not available_indices:
            print("No more unique posts available.")
            break
        post_index = random.choice(list(available_indices))
        posted_indices.add(post_index)

        schedule_single_post(post_index, scheduled_time)

def main():
    print(f"[{datetime.utcnow()} UTC] Fetching posts...")
    posts = fetch_good_posts()
    if not posts:
        print("No good posts found, exiting.")
        return

    print(f"[{datetime.utcnow()} UTC] Scheduling posts...")
    schedule_posts(posts)

    print(f"[{datetime.utcnow()} UTC] Bot running, waiting for scheduled tweets...")
    while True:
        time.sleep(60)  # Keep script alive

if __name__ == '__main__':
    main()


