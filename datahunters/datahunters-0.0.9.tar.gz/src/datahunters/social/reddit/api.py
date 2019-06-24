"""Script for reddit api.
https://praw.readthedocs.io/en/latest/index.html
"""

import praw


class RedditAPI(object):
  """Class for reddit api.
  """

  def __init__(self, client_id, client_secret, user_agent):
    """Get credentials from here:
    https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps
    """
    self.client = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent)
    print("reddit api initialized.")

  def get_subreddit_posts(self, subreddit_id, num=None):
    """Retrieve posts from a subreddit.

    Args:
      subreddit_id: id of a subreddit.
      num: number of posts, use None for all.
    """
    subreddit = self.client.subreddit(subreddit_id)
    posts = subreddit.hot(limit=num)
    all_posts = []
    for post in posts:
      post_obj = {
          "author": post.author,
          "url": post.url,
          "name": post.name,
          "title": post.title,
          "comments": [],
          "comment_num": post.num_comments
      }
      all_posts.append(post_obj)
    return all_posts
