'''
This whole file is garbage

You have been warned
'''
import asyncio

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

        # Fake context
        try:
            with open('youtube_ids.txt', 'r') as f:
                self.youtube_ids = f.read().splitlines()
        except IOError:
            # File will be created later
            self.youtube_ids = []

    def __unload(self):
        self.task.cancel()
        self.session.close()

        with open('youtube_ids.txt', 'w') as f:
            f.writelines(self.youtube_ids)

    def __global_check(self, ctx):
        guild_id = ctx.bot.cfg.get('hstem_guild_id', ctx.bot.cfg['htstem_guild_id'])
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

        channel = discord.utils.find(lambda c: c.id == self.bot.cfg['youtube']['announcement_channel'] or c.name ==
                                     'announcements', self.bot.get_all_channels())

        if channel is None:
            return

        role = discord.utils.find(lambda r: r.id == self.bot.cfg['youtube']['role_id'] or r.name == 'YouTube',
                                  channel.guild.roles)

        while True:
            async with self.session.get(self.bot.cfg['youtube']['feed_url']) as resp:
                data = feedparser.parse(await resp.read())
            videos = data['entries']

            for video in videos:
                href = video['link']

                if href not in self.youtube_ids:
                    self.youtube_ids.append(href)
                    await channel.send('{0.mention} {1} {2}'.format(role, video['title'], href))

            await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(YouTube(bot))
