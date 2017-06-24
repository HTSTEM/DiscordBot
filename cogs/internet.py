from discord.ext import commands
import aiohttp


class Internet:
    def __init__(self, bot):
        self.session = aiohttp.ClientSession(loop=bot.loop)

    def __unload(self):
        self.session.close()

    @commands.command(aliases=['adam'])
    async def dog(self, ctx):
        async with self.session.get('http://random.dog/woof.json') as resp:
            json = await resp.json()
            await ctx.send(json['url'])

    @commands.command(aliases=['b1nzy'])
    async def cat(self, ctx):
        async with self.session.get('http://random.cat/meow') as resp:
            json = await resp.json()
            await ctx.send(json['file'])


def setup(bot):
    bot.add_cog(Internet(bot))
