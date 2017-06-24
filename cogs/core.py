import asyncio
import inspect
import traceback

import discord
from discord.ext import commands
import psutil
import git


class Core:
    '''Core commands'''

    @commands.command()
    async def about(self, ctx):
        '''Info about the bot'''
        def format_commit(commit):
            sha = commit.hexsha[0:6]
            repo = 'https://github.com/HTSTEM/discord-bot/commit/{}'
            return '[`{}`]({}) {}'.format(sha, repo.format(commit.hexsha), commit.message.splitlines()[0])
        repo = git.Repo()
        branch = repo.active_branch
        commits = list(repo.iter_commits(branch, max_count=3))
        log = '\n'.join(map(format_commit, commits))
        memory_usage = round(psutil.Process().memory_full_info().uss / 1024 ** 2, 2)

        embed = discord.Embed(title='About HTStem Bote', description=log)
        embed.add_field(name='Memory Usage', value='{} MB'.format(memory_usage))

        await ctx.send(embed=embed)

    @commands.command(aliases=['quit'])
    @commands.is_owner()
    async def kill(self, ctx):
        '''Disconnects the bot from Discord'''
        await ctx.send('Logging out...')

        await ctx.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        '''Loads an extension'''
        try:
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send('\N{OK HAND SIGN} Loaded cog {} successfully!'.format(cog))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        '''Unloads an extension'''
        try:
            ctx.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send('\N{OK HAND SIGN} Unloaded cog {} successfully!'.format(cog))

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        '''Reloads an extension'''
        try:
            ctx.bot.unload_extension(cog)
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('Failed to load: `{}`\n```py\n{}\n```'.format(cog, e))
        else:
            await ctx.send('\N{OK HAND SIGN} Reloaded cog {} successfully'.format(cog))

    @reload.command(name='all')
    @commands.is_owner()
    async def reload_all(self, ctx):
        '''Reloads all extensions'''
        for extension in ctx.bot.extensions.copy():
            ctx.bot.unload_extension(extension)
            try:
                ctx.bot.load_extension(extension)
            except Exception as e:
                await ctx.send('Failed to load `{}`:\n```py\n{}\n```'.format(extension, e))
                return

        await ctx.send('\N{OK HAND SIGN} Reloaded {} cogs successfully'.format(len(ctx.bot.extensions)))

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        '''Updates the bot from git'''
        await ctx.send('Pulling updates from Git...')

        process = await asyncio.create_subprocess_exec('git', 'pull',
                                                       stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if stdout:
            await ctx.send('**stdout**\n```\n{}\n```'.format(stdout.decode()))
        if stderr:
            await ctx.send('**stderr**\n```\n{}\n```'.format(stderr.decode()))

    @commands.command(aliases=['eval'])
    @commands.is_owner()
    async def debug(self, ctx, *, code: str):
        '''Evaluates code'''
        
        env = {
            'ctx': ctx,
            'bot': ctx.bot,
            'guild': ctx.guild,
            'author': ctx.author,
            'message': ctx.message,
            'channel': ctx.channel
        }
        env.update(globals())
        
        try:
            if code.startswith("await "):
                res = str(await eval(code[6:], env))
            else:
                res = str(eval(code, env))
            
            colour = 0x00FF00
        except:
            res = traceback.format_exc()
            colour = 0xFF0000
            
        embed = discord.Embed(colour = colour,
                              title = code,
                              description = "```py\n{}```".format(res.replace("```", "`` `"))
                             )
        embed.set_author(name=ctx.message.author.display_name,
                         icon_url=ctx.message.author.avatar_url or ctx.message.author.default_avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Core())
