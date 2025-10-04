import praw
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_reddit_client(config: dict):
    """
    Initializes and returns a Reddit API client.

    Args:
        config (dict): A dictionary containing Reddit API credentials.

    Returns:
        praw.Reddit: An authenticated Reddit instance, or None if config is invalid.
    """
    if not all(k in config for k in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]):
        logging.error("Reddit API credentials missing from config.")
        return None

    # Check for placeholder values
    if "YOUR_CLIENT" in config["REDDIT_CLIENT_ID"] or "YOUR_CLIENT" in config["REDDIT_CLIENT_SECRET"]:
        logging.warning("Using placeholder Reddit API credentials. Scraper will not function.")
        return None

    try:
        reddit = praw.Reddit(
            client_id=config["REDDIT_CLIENT_ID"],
            client_secret=config["REDDIT_CLIENT_SECRET"],
            user_agent=config["REDDIT_USER_AGENT"]
        )
        reddit.read_only = True
        logging.info("Successfully authenticated with Reddit API.")
        return reddit
    except Exception as e:
        logging.error(f"Failed to authenticate with Reddit: {e}")
        return None

def scrape_subreddits(reddit: praw.Reddit, subreddits: list[str], limit: int = 25) -> list[dict]:
    """
    Scrapes recent posts from a list of subreddits.

    Args:
        reddit (praw.Reddit): The PRAW client.
        subreddits (list[str]): The names of the subreddits to scrape.
        limit (int): The number of posts to fetch from each subreddit.

    Returns:
        list[dict]: A list of posts, each represented as a dictionary.
    """
    all_posts = []
    if not reddit:
        logging.error("Reddit client is not available. Cannot scrape.")
        # Return mock data for placeholder functionality
        return [
            {"subreddit": "CryptoCurrency", "title": "BTC to the moon!", "score": 150, "num_comments": 45, "url": "mock_url_1"},
            {"subreddit": "Bitcoin", "title": "Is this the end of the bull run?", "score": 20, "num_comments": 100, "url": "mock_url_2"},
        ]

    for sub_name in subreddits:
        try:
            logging.info(f"Scraping hot posts from r/{sub_name}...")
            subreddit = reddit.subreddit(sub_name)
            for post in subreddit.hot(limit=limit):
                all_posts.append({
                    "subreddit": sub_name,
                    "title": post.title,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": post.url
                })
        except Exception as e:
            logging.error(f"Failed to scrape r/{sub_name}: {e}")

    return all_posts