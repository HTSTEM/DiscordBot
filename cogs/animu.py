import random

import discord
import tokage
import functools

from discord.ext import commands
from pybooru import Danbooru

from .util.checks import right_channel
from .util.da import DeviationCollector


class Animu:
    def __init__(self, bot):
        self.bot = bot
        self.mal_client = tokage.Client()

        self.dc = DeviationCollector(bot)
        creds = bot.config['danbooru']
        self.danb = Danbooru('danbooru', username=creds.get('user'), api_key=creds.get('key'))

    async def __local_check(self, ctx):
        return right_channel(ctx)

    @commands.command()
    async def mal(self, ctx, *, query:str):
        '''Search MyAnimeList'''
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

        embed=discord.Embed(
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
    async def wallpaper(self, ctx, *, query:str=''):
        '''Get an anime wallpaper from deviantart'''
        await ctx.send(await self.dc.get_deviation(self.bot.loop, query))

    @commands.command()
    async def danbooru(self, ctx, *tags):
        '''Search Danbooru tags. Safe mode is enabled, but be careful nonetheless'''
        tags = [s.replace(' ', '_') for s in tags]
        if len(tags) > 2:
            await ctx.send('Only 2 tags are allowed, taking the first 2.')
            tags = tags[:2]

        posts = await self.bot.loop.run_in_executor(None,
            functools.partial(self.danb.post_list, tags='rating:s ' + ' '.join(tags), page=1, limit=200)
        )

        post = random.choice(posts)

        try:
            fileurl = 'http://danbooru.donmai.us' + post['file_url']
        except KeyError:
            fileurl = 'http://danbooru.donmai.us' + post['source']

        await ctx.send(f'<{fileurl}>') # antiembed for accidental lewdness prevention


def setup(bot):
    bot.add_cog(Animu(bot))
