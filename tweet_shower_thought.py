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

# Twitter credentials (OAuth1 User authentication)
auth = tweepy.OAuth1UserHandler(
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
)
api = tweepy.API(auth, wait_on_rate_limit=True)

def is_good_post(post):
    return (
        20 < len(post.title) <= 280 and
        post.score >= 50 and
        not post.stickied and
        not post.over_18
    )

def fetch_good_posts():
    subreddit = reddit.subreddit('ShowerThoughts')
    posts = list(subreddit.hot(limit=200))  # more posts for variety
    candidates = [p for p in posts if is_good_post(p)]
    return candidates

def post_thought(thought, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            api.update_status(thought)
            print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] Tweeted: {thought[:60]}...")
            return True
        except tweepy.TweepError as e:
            attempt += 1
            print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] Error tweeting: {e}. Retry {attempt}/{max_retries}")
            time.sleep(10 * attempt)  # exponential backoff
    print(f"Failed to tweet after {max_retries} attempts.")
    return False

def schedule_posts(times_utc, posts):
    posted_indices = set()

    def schedule_single_post(post_index, post_time):
        now = datetime.utcnow()
        wait_seconds = (post_time - now).total_seconds()
        if wait_seconds < 0:
            wait_seconds += 86400  # schedule for next day
        threading.Timer(wait_seconds, lambda: post_thought(posts[post_index].title)).start()
        print(f"Scheduled post #{post_index} at {post_time.strftime('%H:%M:%S')} UTC (in {int(wait_seconds)} seconds)")

    for i, base_hour in enumerate(times_utc):
        # ±3 minutes randomness
        minute_offset = random.randint(-3, 3)
        scheduled_time = datetime.utcnow().replace(hour=base_hour, minute=0, second=0, microsecond=0) + timedelta(minutes=minute_offset)

        # Ensure unique posts
        available_indices = set(range(len(posts))) - posted_indices
        if not available_indices:
            print("Ran out of unique posts!")
            break
        post_index = random.choice(list(available_indices))
        posted_indices.add(post_index)

        schedule_single_post(post_index, scheduled_time)

def main():
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] Fetching good posts from Reddit...")
    posts = fetch_good_posts()
    if len(posts) < 16:
        print(f"Warning: Only found {len(posts)} good posts, will schedule fewer tweets.")

    # 16 best global hours in UTC (approximate peak times)
    best_hours_utc = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 23]

    schedule_count = min(16, len(posts))
    schedule_posts(best_hours_utc[:schedule_count], posts)

    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] Bot is running and waiting for scheduled tweets...")
    while True:
        time.sleep(60)  # keep script alive

if __name__ == "__main__":
    main()




