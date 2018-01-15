import urllib.parse
import random
import time
import aiohttp
import feedparser
import asyncio

from discord.ext import commands
import discord

from .util.data_uploader import DataUploader
from .util.converters import CleanedCode
from .util.checks import right_channel


XKCD_ENDPOINT = 'https://xkcd.com/{}/info.0.json'
XKCD_RSS = 'https://xkcd.com/rss.xml'
BOTE_SPAM = 282500390891683841
VT_API = 'https://www.virustotal.com/vtapi/v2'

cog = None


class Internet:

    @staticmethod
    async def __local_check(ctx):
        return right_channel(ctx)

    def __init__(self, bot):
        self.bot = bot
        self.uploader_client = DataUploader(bot)
        self.xkcd_feed = feedparser.parse(XKCD_RSS)
        self.checker = bot.loop.create_task(self.check_xkcd())

    async def check_xkcd(self):
        while True:
            feed = feedparser.parse(XKCD_RSS, modified=self.xkcd_feed.modified)
            if feed.status == 200:
                if feed.entries[0].link != self.xkcd_feed.entries[0].link:
                    channel = self.bot.get_channel(BOTE_SPAM)
                    if channel is not None:
                        await channel.send(feed.entries[0].link)

                    self.xkcd_feed = feed

            await asyncio.sleep(600)

    @commands.command(aliases=['adam', 'slice', 'jake', 'sills', 'zwei'])
    async def dog(self, ctx):
        """Sends a picture of a random dog"""
        async with ctx.bot.session.get('http://random.dog/woof.json') as resp:
            json = await resp.json()
            await ctx.send(json['url'])

    @commands.command(aliases=['b1nzy'])
    async def cat(self, ctx):
        """Sends a picture of a random cat"""
        async with ctx.bot.session.get('http://random.cat/meow') as resp:
            json = await resp.json()
            await ctx.send(json['file'])

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, query: str):
        """Google for a query"""
        op = urllib.parse.urlencode({'q': query})
        await ctx.send('https://google.com/search?{}&safe=active'.format(op))

    @commands.command(aliases=['wa', 'alpha', 'wolfram_alpha'])
    async def wolfram(self, ctx, *, query: str):
        """Search Wolfram|Alpha for a query"""
        op = urllib.parse.urlencode({'i': query})
        await ctx.send('https://www.wolframalpha.com/input/?{}'.format(op))

    @commands.command()
    async def lucky(self, ctx, *, query: str):
        """I'm feeling lucky. Are you?"""
        op = urllib.parse.urlencode({'q': query})
        async with ctx.bot.session.get('https://google.com/search?{}&safe=active&&btnI'.format(op)) as resp:
            await ctx.send(resp.url)

    @commands.command(aliases=['paste.ee', 'upload'])
    async def paste(self, ctx, *, data: CleanedCode):
        """Upload data to https://paste.ee and return the URL"""

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            title = "{0.display_name}#{0.discriminator}".format(ctx.author)
        else:
            title = "{0.display_name}#{0.discriminator} in #{1}".format(ctx.author, ctx.channel.name)

        url = await self.uploader_client.upload(
                    data,
                    title
                )
        await ctx.send('{0.mention} {1}'.format(ctx.author, url))
        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await ctx.message.delete()

    async def post_comic(self, ctx: commands.Context, metadata: 'Dict[str, Any]', comic_number: int):
        embed = discord.Embed(title='#{}'.format(metadata['num']), description=metadata['safe_title'],
                              url='https://xkcd.com/{}/'.format(metadata['num']), colour=0xFFFFFF)
        embed.set_image(url=metadata['img'])
        embed.set_footer(text=metadata['alt'])

        await ctx.send(embed=embed)

    async def fetch_comic_data(self, number=None, *, latest=False):
        async with self.bot.session.get(XKCD_ENDPOINT.format(number if not latest else '')) as resp:
            return await resp.json()

    @commands.group(invoke_without_command=True)
    async def xkcd(self, ctx, *, comic_number: int):
        """ Shows an XKCD comic by comic number. """
        latest = await self.fetch_comic_data(latest=True)

        if comic_number > latest['num']:
            await ctx.send('Woah! Steady there tiger! There are only {} comics available. :cry:'.format(latest['num']))
            return
        elif comic_number < 1:
            await ctx.send('"Get strip number {}," they said, "It\'ll be easy."'.format(comic_number))
            return
        elif comic_number == 404:
            await ctx.send('`404`.. Really? What were you expecting??')
            return

        target = await self.fetch_comic_data(comic_number)

        await self.post_comic(ctx, target, comic_number)

    @xkcd.command()
    async def latest(self, ctx):
        """ Shows the latest XKCD comic. """
        latest = await self.fetch_comic_data(latest=True)
        await self.post_comic(ctx, latest, latest['num'])

    @xkcd.command()
    async def random(self, ctx):
        """ Shows a random XKCD comic. """
        latest = await self.fetch_comic_data(latest=True)
        comic_number = random.randint(1, latest['num'])
        target = await self.fetch_comic_data(comic_number)

        await self.post_comic(ctx, target, comic_number)

    @commands.command(aliases=['latency'])
    async def ping(self, ctx):
        """Views websocket and message send latency."""
        # Websocket latency
        results = []
        for shard in ctx.bot.shards.values():
            ws_before = time.monotonic()
            await (await shard.ws.ping())
            ws_after = time.monotonic()
            results.append(round((ws_after - ws_before) * 1000))

        # Message send latency
        rtt_before = time.monotonic()
        message = await ctx.send('Ping...')
        rtt_after = time.monotonic()

        rtt_latency = round((rtt_after - rtt_before) * 1000)

        await message.edit(content='WS: **{0} ms**\nRTT: **{1} ms**'.format(', '.join(map(str, results)), rtt_latency))

    @commands.command(aliases=['scan'])
    @commands.cooldown(4, 60)
    async def virustotal(self, ctx, url):
        """Scan a url"""
        key_file = self.bot.config['virustotal'].get('key_file')
        with open(key_file) as f:
            key = f.read().split('\n')[0].strip()

        params = {'apikey': key, 'url': url}
        async with aiohttp.ClientSession() as session:
            async with session.post(VT_API+'/url/scan', data=params) as request:
                response = await request.json()

        if response['response_code'] == -1:
            await ctx.send('Invalid url.')
        elif 'permalink' not in response:
            await ctx.send('Search failed. Are you sure you entered a valid url?')
        else:
            await ctx.send(f'Scan results found.\n{response["permalink"]}')


def setup(bot):
    global cog
    bot.add_cog(Internet(bot))
    cog = bot.cogs['Internet']

def teardown(bot):
    global cog
    cog.checker.close()
