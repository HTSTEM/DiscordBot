import urllib.parse

from discord.ext import commands
import aiohttp


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


def setup(bot):
    bot.add_cog(Internet(bot))
