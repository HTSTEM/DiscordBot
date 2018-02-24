import random
import io
import os

import discord
import tokage
import functools

from discord.ext import commands
from pybooru import Danbooru
from pybooru.exceptions import PybooruHTTPError
import pixiv

from .util.checks import right_channel
from .util.da import DeviationCollector


class Animu:
    AWWNIME = 'https://www.reddit.com/r/awwnime.json?limit={}'

    def __init__(self, bot):
        self.bot = bot
        self.mal_client = tokage.Client()

        self.dc = DeviationCollector(bot)

        creds = bot.config['danbooru']
        key_file = creds.get('key_file')
        with open(key_file) as f:
            key = f.read().split('\n')[0].strip()

        self.danb = Danbooru('danbooru', username=creds.get('user'), api_key=key)

        creds = bot.config['pixiv']
        pwd_file = creds.get('pwd_file')
        with open(pwd_file) as f:
            pwd = f.read().split('\n')[0].strip()

#        self.pixiv_ = pixiv.login(creds.get('user'), pwd)

    @staticmethod
    async def __local_check(ctx):
        return right_channel(ctx)

    @commands.command()
    async def mal(self, ctx, *, query: str):
        """Search MyAnimeList"""
        try:
            anime_id = await self.mal_client.search_id('anime', query)
        except tokage.errors.TokageNotFound:
            anime_id = None

        if anime_id is None:
            return await ctx.send('No anime found. Sorry.')

        anime = await self.mal_client.get_anime(anime_id)

        synopsis = anime.synopsis

        if len(synopsis) > 500:
            synopsis = synopsis[:500].strip()
            synopsis += f'... [Read more]({anime.link})'

        embed = discord.Embed(
            title=anime.japanese_title,
            url=anime.link,
            description=f'**{anime.title}** ({anime.rating})\n{synopsis}')
        embed.set_thumbnail(url=anime.image)
        embed.add_field(name="Score", value=f'{anime.score[0]} ({anime.score[1]} reviews)', inline=True)
        embed.add_field(name="Rank", value=f'#{anime.rank}', inline=True)
        embed.add_field(name="Popularity", value=f'#{anime.popularity}', inline=True)
        embed.add_field(name="Episodes", value=anime.episodes, inline=True)
        embed.add_field(name="Status", value=anime.status, inline=True)
        embed.add_field(name="Duration", value=anime.duration, inline=True)
        embed.add_field(name="First Aired", value=anime.air_start, inline=True)
        embed.add_field(name="Finished Airing", value=anime.air_end, inline=True)
        embed.set_footer(text=' | '.join(anime.genres))

        await ctx.send(embed=embed)

    @commands.command(aliases=['wall'])
    async def wallpaper(self, ctx, *, query: str=''):
        """Get an anime wallpaper from deviantart"""
        await ctx.send(await self.dc.get_deviation(self.bot.loop, query))

    @commands.command()
    async def danbooru(self, ctx, *tags):
        """
        Search Danbooru tags.
        Safe mode is enabled, but be careful.
        """
        hide = True
        if tags and tags[0] == 'lesssafe':
            hide = False
            tags = tags[1:]

        tags = [s.replace(' ', '_') for s in tags]
        if len(tags) > 2:
            await ctx.send('Only 2 tags are allowed, taking the first 2.')
            tags = tags[:2]

        try:
            posts = await self.bot.loop.run_in_executor(
                None,
                functools.partial(self.danb.post_list, tags='rating:s ' + ' '.join(tags), page=1, limit=200)
            )
        except (KeyError, PybooruHTTPError):
            return await ctx.send('Uh oh, something happened. Are your tags valid?')

        if not posts:
            return await ctx.send('No results found.')

        post = random.choice(posts)

        try:
            fileurl = 'http://danbooru.donmai.us' + post['file_url']
        except KeyError:
            fileurl = 'http://danbooru.donmai.us' + post['source']

        if hide:
            return await ctx.send(f'<{fileurl}>')  # antiembed for accidental lewdness prevention

        return await ctx.send(fileurl)

    @commands.command(aliases=['moe'])
    async def awwnime(self, ctx, limit:int=100):
        """Sometimes we all just need a little moe."""
        async with ctx.typing():
            async with self.bot.session.get(self.AWWNIME.format(limit)) as resp:
                dat = await resp.json()
            dat = dat.get('data', {}).get('children', [])
            dat = [
                i for i in dat if i.get('data', {}).get('post_hint', '') == 'image' and not i.get('data', {}).get('over_18', True)
            ]
            if not dat:
                return await ctx.send('I failed to find moe (somehow). Try again later.')

            dat = random.choice(dat).get('data', {})

            if 'url' not in dat:
                return await ctx.send('Something went very wrong. Please try again.')

            msg = f'**{dat["title"]}**:\n{dat["url"]}'
            await ctx.send(msg)

    @commands.command()
    async def pixiv(self, ctx, *, query: str):
        """Find some fun things on Pixiv"""
        return
        async with ctx.typing():
            r = self.pixiv_.search(query)
            if not r:
                return await ctx.send('No results found.')

            await ctx.send(f'I found: https://pixiv.net/i/{random.choice(r).id}')

    @commands.command()
    async def pixivfr(self, ctx, *, query: str):
        """Find some fun things on Pixiv (full-res)"""

        async with ctx.typing():
            r = self.pixiv_.search(query)
            if not r:
                return await ctx.send('No results found.')

            fn = random.choice(r).save()

            with open(fn, 'rb') as f:
                await ctx.send(f'I found:', file=discord.File(f))
            os.remove(fn)


def setup(bot):
    bot.add_cog(Animu(bot))
