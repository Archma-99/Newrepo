import os
import sys
import praw
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bitcoin_predictor.storage.db_connection import get_db_connection
from bitcoin_predictor.processing.sentiment_analysis import get_sentiment_score

# Reddit API Credentials
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "bitcoin_predictor_v1")

def get_reddit_instance():
    """Initializes and returns a PRAW instance for Reddit."""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
        print("Reddit API credentials are not set. Skipping Reddit data ingestion.")
        return None

    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def fetch_reddit_posts(subreddit_name, limit=25):
    """Fetches posts from a given subreddit."""
    reddit = get_reddit_instance()
    if not reddit:
        return []

    posts = []
    subreddit = reddit.subreddit(subreddit_name)
    for post in subreddit.hot(limit=limit):
        posts.append({
            "title": post.title,
            "content": post.selftext,
            "author": str(post.author),
            "url": post.url,
            "timestamp": datetime.fromtimestamp(post.created_utc)
        })
    return posts

def insert_social_media_data(conn, posts, platform):
    """Inserts social media posts into the database."""
    with conn.cursor() as cur:
        for post in posts:
            # Combine title and content for sentiment analysis
            full_text = f"{post['title']} {post['content']}"
            sentiment = get_sentiment_score(full_text)

            cur.execute(
                """
                INSERT INTO social_posts (timestamp, platform, author, content, sentiment_score, url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (post['timestamp'], platform, post['author'], full_text, sentiment, post['url'])
            )
    conn.commit()

def main():
    """Main function to fetch and store social media data."""
    print("Fetching social media data...")
    conn = get_db_connection()
    if not conn:
        print("Database connection failed. Aborting social media data ingestion.")
        return

    # Fetch from Reddit
    reddit_posts = fetch_reddit_posts("Bitcoin", limit=50)
    if reddit_posts:
        print(f"Fetched {len(reddit_posts)} posts from Reddit.")
        insert_social_media_data(conn, reddit_posts, "Reddit")
        print("Reddit data inserted successfully.")

    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()