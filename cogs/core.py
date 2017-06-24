import asyncio
import inspect

from discord.utils import oauth_url
from discord.ext import commands
import psutil
import git


class Core:
    '''
    Core commands
    '''
    @commands.command()
    async def info(self, ctx):
        '''Info about the bot'''
        # TODO Embeds?
        repo = git.Repo()
        branch = repo.active_branch
        commits = list(repo.iter_commits(branch, max_count=3))

        memory = psutil.Process().memory_full_info().uss / 1024 ** 2

        log = ''

        for commit in commits:
            log += '[{0}] {1}\n'.format(commit.hexsha[0:6], commit.message.splitlines()[0])

        app_info = await ctx.bot.application_info()
        invite = oauth_url(app_info.id)

        fmt = ('Latest commits:\n{}\n'
               'Memory Usage:\n{}\n'
               'Bot Invite:\n{}')
        await ctx.send(fmt.format(log, memory, invite))

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx):
        '''
        Disconnects the bot from Discord
        '''
        await ctx.send('Logging out...')

        await ctx.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        '''
        Loads an extension
        '''
        try:
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send('\N{OK HAND SIGN} Loaded cog {} successfully!'.format(cog))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        '''
        Unloads an extension
        '''
        try:
            ctx.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send('\N{OK HAND SIGN} Unloaded cog {} successfully!'.format(cog))

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        '''
        Reloads an extension
        '''
        try:
            ctx.bot.unload_extension(cog)
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send('\N{OK HAND SIGN} Reloaded cog {} successfully'.format(cog))

    @reload.command(name='all')
    @commands.is_owner()
    async def _all(self, ctx):
        '''
        Reloads all extensions
        '''
        for extension in ctx.bot.extensions.copy():
            ctx.bot.unload_extension(extension)
            try:
                ctx.bot.load_extension(extension)
            except Exception as e:
                pass  # TODO logging
            else:
                pass  # TODO logging

        await ctx.send('\N{OK HAND SIGN} Reloaded {} cogs successfully'.format(len(ctx.bot.extensions)))

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        '''
        Updates the bot from git
        '''
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
        fmt = '```py\n{}\n```'
        result = None

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
            result = eval(code, env)

            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(fmt.format(type(e).__name__ + ': ' + str(e)))
        else:
            await ctx.send(fmt.format(result))


def setup(bot):
    bot.add_cog(Core())
