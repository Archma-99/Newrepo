import os
import sys
import praw
from datetime import datetime
import pytz

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from project.db.db_handler import connect_to_db
from project.utils.sentiment import get_sentiment_score

# Reddit API Credentials from environment variables
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "bitcoin_predictor/v1.0")

def get_reddit_instance():
    """Initializes and returns a PRAW instance if credentials are available."""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
        return None

    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def fetch_posts_from_subreddit(subreddit_name, limit=25):
    """Fetches top posts from a given subreddit."""
    reddit = get_reddit_instance()
    if not reddit:
        return []

    posts = []
    subreddit = reddit.subreddit(subreddit_name)
    try:
        for post in subreddit.hot(limit=limit):
            posts.append({
                "title": post.title,
                "content": post.selftext,
                "url": post.url,
                "timestamp": datetime.fromtimestamp(post.created_utc, tz=pytz.utc)
            })
    except Exception as e:
        print(f"Failed to fetch posts from Reddit: {e}")
    return posts

def insert_social_sentiment_data(conn, posts, platform):
    """Inserts social media posts and their sentiment into the database."""
    with conn.cursor() as cur:
        for post in posts:
            full_text = f"{post['title']} {post['content']}"
            sentiment = get_sentiment_score(full_text)

            cur.execute(
                """
                INSERT INTO social_sentiment (timestamp, platform, content, sentiment_score, url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (post['timestamp'], platform, full_text, sentiment, post['url'])
            )
    conn.commit()

def main():
    """Main function to fetch and store social media data."""
    reddit = get_reddit_instance()
    if not reddit:
        print("Reddit API credentials not set. Skipping social media data collection.")
        return

    print("Fetching social media data from Reddit...")
    conn = connect_to_db()
    if not conn:
        print("Database connection failed. Aborting social media ingestion.")
        return

    try:
        reddit_posts = fetch_posts_from_subreddit("Bitcoin", limit=50)
        if reddit_posts:
            print(f"-> Fetched {len(reddit_posts)} posts from r/Bitcoin.")
            insert_social_sentiment_data(conn, reddit_posts, "Reddit")
            print("   Reddit data stored successfully.")
    except Exception as e:
        print(f"An error occurred during social media ingestion: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()