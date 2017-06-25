import urllib.parse
import time
import os

from discord.ext import commands
import aiohttp
import discord
import random


class Internet:
    def __init__(self, bot):
        self.session = aiohttp.ClientSession(loop=bot.loop)

    def __unload(self):
        self.session.close()

    @commands.command(aliases=['adam', 'slice', 'jake'])
    async def dog(self, ctx):
        '''Sends a picture of a random dog'''
        async with self.session.get('http://random.dog/woof.json') as resp:
            json = await resp.json()
            await ctx.send(json['url'])

    @commands.command(aliases=['b1nzy'])
    async def cat(self, ctx):
        '''Sends a picture of a random cat'''
        async with self.session.get('http://random.cat/meow') as resp:
            json = await resp.json()
            await ctx.send(json['file'])

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, query: str):
        '''Google for a query'''
        op = urllib.parse.urlencode({'q': query})
        await ctx.send('https://google.com/search?{}&safe=active'.format(op))

    @commands.command(aliases=['wa', 'alpha', 'wolfram_alpha'])
    async def wolfram(self, ctx, *, query: str):
        '''Search Wolfram|Alpha for a query'''
        op = urllib.parse.urlencode({'i': query})
        await ctx.send('https://www.wolframalpha.com/input/?{}'.format(op))

    @commands.command()
    async def lucky(self, ctx, *, query: str):
        '''I'm feeling lucky. Are you?'''
        op = urllib.parse.urlencode({'q': query})
        async with self.session.get('https://google.com/search?{}&safe=active&&btnI'.format(op)) as resp:
            await ctx.send(resp.url)

    @commands.command(aliases=['haste', 'paste'])
    async def hastebin(self, ctx, *, data: str):
        '''Upload data to https://hastebin.com and return the URL'''
        async with self.session.post('https://hastebin.com/documents', data=data.encode(), headers={'content-type': 'application/json'}) as resp:
            await ctx.send('{0.mention} https://hastebin.com/{}'.format(ctx.author, (await resp.json())["key"]))
            await ctx.message.delete()

    @commands.group(invoke_without_command=True)
    async def xkcd(self, ctx, *, comic_number: str):
        url = 'https://xkcd.com/{}/info.0.json'
    
        try:
            comic_number = int(comic_number)
        except ValueError:
            await ctx.send('Does that look like a number to you? Ehh?')
            return
        
        async with self.session.get(url.format('')) as resp:
            latest = await resp.json()
            
        if comic_number > latest['num']:
            await ctx.send('Woah! Steady there tiger! There are only {} xkcds avaliable. :cry:'.format(latest['num']))
            return
        if comic_number < 1:
            await ctx.send('"Get strip number {}," they said, "It\'ll be easy."'.format(comic_number))
            return
        
        if not os.path.exists('xkcd'):
            os.mkdir('xkcd')
        
        async with self.session.get(url.format(comic_number)) as resp:
            target = await resp.json()
        
        if not '{}.png'.format(comic_number) in os.listdir('xkcd'):
            async with self.session.get(target['img']) as resp:
                img = await resp.read()
                with open('xkcd/{}.png'.format(comic_number), 'wb') as img_file:
                    img_file.write(img)

        await ctx.send("**{}:**\n*{}*".format(target['safe_title'], target['alt']), file=discord.File('xkcd/{}.png'.format(comic_number)))

    @xkcd.command()
    async def latest(self, ctx):
        url = 'https://xkcd.com/{}/info.0.json'
        
        async with self.session.get(url.format('')) as resp:
            latest = await resp.json()
        
        if not os.path.exists('xkcd'):
            os.mkdir('xkcd')
        
        if not '{}.png'.format(latest['num']) in os.listdir('xkcd'):
            async with self.session.get(latest['img']) as resp:
                img = await resp.read()
                with open('xkcd/{}.png'.format(latest['num']), 'wb') as img_file:
                    img_file.write(img)

        await ctx.send("**{}:**\n*{}*".format(latest['safe_title'], latest['alt']), file=discord.File('xkcd/{}.png'.format(latest['num'])))

    @xkcd.command()
    async def random(self, ctx):
        url = 'https://xkcd.com/{}/info.0.json'
        
        async with self.session.get(url.format('')) as resp:
            latest = await resp.json()
            
        comic_number = random.randint(1, latest['num'])
        
        if not os.path.exists('xkcd'):
            os.mkdir('xkcd')
        
        async with self.session.get(url.format(comic_number)) as resp:
            target = await resp.json()
        
        if not '{}.png'.format(comic_number) in os.listdir('xkcd'):
            async with self.session.get(target['img']) as resp:
                img = await resp.read()
                with open('xkcd/{}.png'.format(comic_number), 'wb') as img_file:
                    img_file.write(img)

        await ctx.send("**{}:**\n*{}*".format(target['safe_title'], target['alt']), file=discord.File('xkcd/{}.png'.format(comic_number)))
        
    @commands.command(aliases=['latency'])
    async def ping(self, ctx):
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


def setup(bot):
    bot.add_cog(Internet(bot))
