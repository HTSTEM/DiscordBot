import hashlib

import discord
from discord.ext import commands


class Hashing:
    async def hash(self, data: str, hashlib_method: str, pretty_type: str):
        def hash_func():
            func = getattr(hashlib, hashlib_method)
            return func(data.encode('utf-8')).hexdigest()
        embed = discord.Embed(colour=0xAAFF00, title='{} of `{}`'.format(pretty_type, data),
                              description='```\n{}\n```'.format(hash_func()))
        return embed

    @commands.command(aliases=['hash'])
    async def md5(self, ctx, *, to_hash: str):
        '''Compute the MD5 hash of a string'''
        await ctx.send(embed=await self.hash(to_hash, 'md5', 'MD5 hash'))
    
    @commands.command()
    async def sha1(self, ctx, *, to_hash: str):
        '''Compute the SHA1 hash of a string'''
        await ctx.send(embed=await self.hash(to_hash, 'sha1', 'SHA1 hash'))
    
    @commands.command()
    async def sha256(self, ctx, *, to_hash: str):
        '''Compute the SHA256 hash of a string'''
        await ctx.send(embed=await self.hash(to_hash, 'sha256', 'SHA256 hash'))
    
    @commands.command()
    async def sha512(self, ctx, *, to_hash: str):
        '''Compute the SHA512 hash of a string'''
        await ctx.send(embed=await self.hash(to_hash, 'sha512', 'SHA512 hash'))


def setup(bot):
    bot.add_cog(Hashing())
