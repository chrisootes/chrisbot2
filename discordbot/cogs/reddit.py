import discord
from discord.ext import commands

import asyncio
import logging
import math
import random
import praw

from discordbot.utils.config import config

logger = logging.getLogger(__name__)

reddit = praw.Reddit(
    client_id=config.get('reddit', 'client_id'),
    client_secret=config.get('reddit', 'client_secret'),
    user_agent=config.get('reddit', 'user_agent')
)

class RedditCommands:
    """
    Reddit commands for discord bot.
    https://github.com/chrisootes/chrisbot2
    """
    def __init__(self, bot):
        self.bot = bot

        logger.info("reddit read only is {0}".format(reddit.read_only))

    @commands.command(pass_context=True)
    async def reddit(self, ctx, reddit_sub : str, reddit_limit = 10):
        """Posts one of top 10 hottest link from the given subreddit."""
        logger.info("reddit command issued by {0}".format(ctx.message.author.name))

        reddit_top = reddit.subreddit(reddit_sub).hot(limit=reddit_limit)
        reddit_random = math.floor(random.random()*reddit_limit)

        logger.info("reddit sub is {0}".format(reddit_sub))
        logger.info("reddit post number is {0}".format(reddit_random))

        reddit_counter = 0
        for reddit_post in reddit_top:
            if(reddit_counter == reddit_random):
                logger.info("reddit post url is {0}".format(reddit_post.url))
                await ctx.send(reddit_post.url)
                return
            else:
                reddit_counter += 1

        await ctx.send("This subreddit is maybe empty")

def setup(bot):
    bot.add_cog(RedditCommands(bot))
