import os
import praw
from datetime import datetime, timedelta


def get_reddit_posts(subreddits, stock_symbol, limit=100, days=30):
    """
    Get posts from a specific subreddit containing the stock symbol within the last specified days.
    """
    reddit = praw.Reddit(
        client_id="gqsZTfPeXWiDp4tzVvUaIw",
        client_secret="9EVIT1W1KrXhrCCguYvO0TqcpXwpHQ",
        user_agent="ashu llm",
        password="Ashu@1510",
        username="ashutosh1510",
    )
    posts = []

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        for post in subreddit.search(stock_symbol, sort='new', time_filter='month', limit=limit):
            post_date = datetime.utcfromtimestamp(post.created_utc)
            if start_date <= post_date <= end_date:
                posts.append(post.title)
    return posts
subreditlist=['wallstreetbets','StockMarket_Update', 'stocks', 'investing','personalfinance','StockMarket']
x=get_reddit_posts(subreditlist,"appl")
print(x)