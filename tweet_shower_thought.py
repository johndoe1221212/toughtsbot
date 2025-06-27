import praw
import tweepy
import random

# Reddit credentials
reddit = praw.Reddit(
    client_id='ezPbHCuMJj1ChN3AgnnNsQ',
    client_secret='Fo-_z2FPZU7cnkASLULylNDEJ0jCMQ',
    user_agent='ShowerThoughtsBot by u/Typical_Farm6742'
)

# Twitter credentials (Tweepy v2 client)
consumer_key = 'JYAsQiOuOQQavkxN4B1Uf1kch'
consumer_secret = '9kEoZ5UfxsDok8OP6QY9GdtxaoNEQPBTugcdMVP8yBtdNbE05Q'
access_token = '1938321275136442368-zGLGpqRpoU6yolyUMPXsVUZdMjwgXS'
access_token_secret = 'Pu0O9kSnDH6rPykLzzQ0eoIyDHAsnQePOtuzCJve8XLrN'

# Initialize Tweepy Client (v2)
client = tweepy.Client(
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

def main():
    subreddit = reddit.subreddit('ShowerThoughts')
    posts = list(subreddit.hot(limit=100))
    candidates = [p for p in posts if is_good_post(p)]

    if not candidates:
        print("No good posts found.")
        return

    thought = random.choice(candidates).title

    try:
        response = client.create_tweet(text=thought)
        print(f"✅ Tweeted: {thought}\n🆔 Tweet ID: {response.data['id']}")
    except tweepy.TweepyException as e:
        print("❌ Error tweeting:", e)

if __name__ == '__main__':
    main()



