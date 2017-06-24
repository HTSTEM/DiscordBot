import hashlib

import discord
from discord.ext import commands


class Hashing:
    @commands.command(aliases=['hash'])
    async def md5(self, ctx, *, to_hash: str):
        '''Compute the MD5 hash of a string'''

        embed = discord.Embed(colour = 0xAAFF00,
                              title = "MD5 Hash of `{}`:".format(to_hash),
                              description = "```\n{}```".format(hashlib.md5(to_hash.encode("utf-8")).hexdigest())
                             )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def sha1(self, ctx, *, to_hash: str):
        '''Compute the SHA1 hash of a string'''

        embed = discord.Embed(colour = 0xAAFF00,
                              title = "SHA1 Hash of `{}`:".format(to_hash),
                              description = "```\n{}```".format(hashlib.sha1(to_hash.encode("utf-8")).hexdigest())
                             )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def sha256(self, ctx, *, to_hash: str):
        '''Compute the SHA256 hash of a string'''

        embed = discord.Embed(colour = 0xAAFF00,
                              title = "SHA256 Hash of `{}`:".format(to_hash),
                              description = "```\n{}```".format(hashlib.sha256(to_hash.encode("utf-8")).hexdigest())
                             )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def sha512(self, ctx, *, to_hash: str):
        '''Compute the SHA512 hash of a string'''

        embed = discord.Embed(colour = 0xAAFF00,
                              title = "SHA512 Hash of `{}`:".format(to_hash),
                              description = "```\n{}```".format(hashlib.sha512(to_hash.encode("utf-8")).hexdigest())
                             )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Hashing())
