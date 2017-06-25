'''
This whole file is garbage

You have been warned
'''
import asyncio
import os

from discord.ext import commands
import feedparser
import aiohttp
import discord


class YouTube:
    '''
    Youtube related commands
    '''
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.task = self.bot.loop.create_task(self.youtube_feed())

    def __unload(self):
        self.task.cancel()
        self.session.close()

    def __global_check(self, ctx):
        guild_id = ctx.bot.cfg.get('hstem_guild_id', None) or ctx.bot.cfg['debug_channel_id']
        return ctx.guild.id == guild_id if not ctx.bot.debug else True

    @commands.group(aliases=['yt'])
    async def youtube(self, ctx):
        '''Commands related to the YouTube feed.'''

    @youtube.command()
    async def on(self, ctx):
        '''Add the YouTube role'''
        role = discord.utils.find(lambda r: r.id == ctx.bot.cfg['youtube']['role_id'] or r.name == 'YouTube',
                                  ctx.guild.roles)
        await ctx.author.add_roles(role)

    @youtube.command()
    async def off(self, ctx):
        '''Remove the YouTube role'''
        role = discord.utils.find(lambda r: r.id == ctx.bot.cfg['youtube']['role_id'] or r.name == 'YouTube',
                                  ctx.guild.roles)
        await ctx.author.remove_roles(role)

    async def youtube_feed(self):
        await self.bot.wait_until_ready()

        # Fix this
        while True:
            if not os.path.exists("videoURLS.txt"):
                open("videoURLS.txt", "w").close()

            feed = feedparser.parse(self.bot.cfg['youtube']['feed_url'])
            videos = feed["entries"]

            with open("videoURLS.txt") as f:
                urls = f.read().split("\n")

            for v in videos:
                href = v["link"]
                if href not in urls:
                    title = v["title"]
                    print("New video: %s - %s" % (title, href))
                    channel = self.bot.get_channel(self.bot.cfg['youtube']['announcement_channel'])
                    await channel.send("@here `carykh` has uploaded a new YouTube video!\n\"{}\" - {}".format(title, href))
                    urls.append(href)

            with open("videoURLS.txt", "w") as f:
                f.writelines(urls)

            await asyncio.sleep(15)


def setup(bot):
    bot.add_cog(YouTube(bot))
