import praw
import tweepy
import random
import time
from datetime import datetime, timedelta, timezone
import threading

# Reddit credentials (hardcoded)
reddit = praw.Reddit(
    client_id='ezPbHCuMJj1ChN3AgnnNsQ',
    client_secret='Fo-_z2FPZU7cnkASLULylNDEJ0jCMQ',
    user_agent='ShowerThoughtsBot by u/Typical_Farm6742'
)

# Twitter credentials (hardcoded)
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAL0Y2wEAAAAAS6rOXdIUA6or9yp0KwkYJ7S8tbQ%3Daf3RSaYf3a8cQyalKoayZ3mF0rARL1GVOlFaML4zB8CrcrU2jO'
consumer_key = 'JYAsQiOuOQQavkxN4B1Uf1kch'
consumer_secret = '9kEoZ5UfxsDok8OP6QY9GdtxaoNEQPBTugcdMVP8yBtdNbE05Q'
access_token = '1938321275136442368-zGLGpqRpoU6yolyUMPXsVUZdMjwgXS'
access_token_secret = 'Pu0O9kSnDH6rPykLzzQ0eoIyDHAsnQePOtuzCJve8XLrN'

# Initialize Tweepy Client (v2)
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
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
    posts = list(subreddit.hot(limit=200))  # get more posts for variety
    candidates = [p for p in posts if is_good_post(p)]
    return candidates

def post_thought(thought):
    try:
        response = client.create_tweet(text=thought)
        print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}] Tweeted: {thought[:60]}...")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}] Error tweeting:", e)

def schedule_posts(times_utc, posts):
    posted_indices = set()

    def schedule_single_post(post_index, post_time):
        now = datetime.now(timezone.utc)
        wait_seconds = (post_time - now).total_seconds()
        if wait_seconds < 0:
            # Schedule for next day if time passed
            wait_seconds += 86400
        threading.Timer(wait_seconds, lambda: post_thought(posts[post_index].title)).start()
        print(f"Scheduled post #{post_index} at {post_time.strftime('%H:%M:%S %Z')} UTC (in {int(wait_seconds)} seconds)")

    for i, base_hour in enumerate(times_utc):
        minute_offset = random.randint(-3, 3)
        scheduled_time = datetime.now(timezone.utc).replace(hour=base_hour, minute=0, second=0, microsecond=0) + timedelta(minutes=minute_offset)

        available_indices = set(range(len(posts))) - posted_indices
        if not available_indices:
            print("Ran out of unique posts!")
            break
        post_index = random.choice(list(available_indices))
        posted_indices.add(post_index)

        schedule_single_post(post_index, scheduled_time)

def main():
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}] Fetching good posts from Reddit...")
    posts = fetch_good_posts()
    if len(posts) < 16:
        print(f"Warning: Only found {len(posts)} good posts to tweet.")

    best_hours_utc = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 23]

    print(f"Scheduling up to 16 tweets daily at best global engagement hours with ±3 minutes randomness...")
    schedule_posts(best_hours_utc[:min(16, len(posts))], posts)

    print("Bot is running and waiting for scheduled tweets...")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()





