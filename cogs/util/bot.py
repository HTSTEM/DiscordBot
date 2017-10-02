import traceback
import datetime
import logging
import aiohttp
import sqlite3
import sys
import re

from discord.ext import commands
import ruamel.yaml as yaml
import discord

from .ruleBot.rulebot import RuleBot
from .data_uploader import DataUploader
from .checks import right_channel


class HelperBodge():
    def __init__(self, data):
        self.data = data
    def format(self, arg):
        return self.data.format(arg.replace('@', '@\u200b'))


class HTSTEMBote(commands.AutoShardedBot):
    class SilentCheckFailure(commands.CheckFailure): pass
    
    def __init__(self, log_file=None, *args, **kwargs):
        self.debug = False
        self.config = {}
        with open('config.yml', 'r') as f:
            self.config = yaml.load(f, Loader=yaml.Loader)

        logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s] %(message)s')
        self.logger = logging.getLogger('bot')

        super().__init__(
            command_prefix='sb?',
            command_not_found=HelperBodge('No command called `{}` found.'),
            *args,
            **kwargs
        )

        self.session = aiohttp.ClientSession(loop=self.loop)

        self.uploader_client = DataUploader(self)
        
        self.database = sqlite3.connect("memos.sqlite")
        if not self._check_table_exists("memos"):
            dbcur = self.database.cursor()
            dbcur.execute('''
                CREATE TABLE memos(memo TEXT, user_id INTEGER, length INTEGER, start_time INTEGER)''')
            dbcur.close()
            self.database.commit()
        
        self.rule_bot = RuleBot()
    
    def _check_table_exists(self, tablename):
        dbcur = self.database.cursor()
        dbcur.execute('''
            SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';
            '''.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone():
            dbcur.close()
            return True

        dbcur.close()
        return False

    async def on_message(self, message):
        await self.rule_bot.on_message(message)
    
        channel = message.channel

        if message.content.startswith('sb?help'):
            message.content = message.clean_content
        
        # Bypass on direct messages
        if isinstance(channel, discord.DMChannel):
            await self.process_commands(message)
            return

        await self.process_commands(message)

    async def notify_devs(self, lines, message: discord.Message = None):
        # form embed
        embed = discord.Embed(colour=0xFF0000, title='An error occurred \N{FROWNING FACE WITH OPEN MOUTH}')

        if message is not None:
            if len(message.content) > 400:
                url = await self.uploader_client.upload(message.content, 'Message triggering error')
                embed.add_field(name='Command', value=url, inline=False)
            else:
                embed.add_field(name='Command', value='```\n{}\n```'.format(message.content), inline=False)
            embed.set_author(name=message.author, icon_url=message.author.avatar_url_as(format='png'))

        embed.set_footer(text='{} UTC'.format(datetime.datetime.utcnow()))

        error_message = ''.join(lines)
        if len(error_message) > 1000:
            url = await self.uploader_client.upload(error_message, 'Error')

            embed.add_field(name='Error', value=url, inline=False)
        else:
            embed.add_field(name='Error', value='```py\n{}\n```'.format(''.join(lines), inline=False))

        # loop through all developers, send the embed
        for dev in self.config.get('ids', {}).get('developers', []):
            dev = self.get_user(dev)

            if dev is None:
                self.logger.warning('Could not get developer with an ID of {0.id}, skipping.'.format(dev))
                continue
            try:
                await dev.send(embed=embed)
            except Exception as e:
                self.logger.error('Couldn\'t send error embed to developer {0.id}. {1}'
                                  .format(dev, type(e).__name__ + ': ' + str(e)))

    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        if isinstance(exception, commands.CommandInvokeError):
            # all exceptions are wrapped in CommandInvokeError if they are not a subclass of CommandError
            # you can access the original exception with .original
            original = exception.original
            if isinstance(original, discord.Forbidden):
                # permissions error
                try:
                    await ctx.send('Permissions error: `{}`'.format(exception))
                except discord.Forbidden:
                    # we can't send messages in that channel
                    pass
                
            elif isinstance(original, discord.HTTPException) and original.status == 400:
                try: await ctx.send('Congratulations! I can\'t send that message.')
                except discord.Forbidden: pass
            
            else:
                # Print to log then notify developers
                lines = traceback.format_exception(type(exception),
                                                exception,
                                                exception.__traceback__)

                self.logger.error(''.join(lines))
                await self.notify_devs(lines, ctx.message)

        elif isinstance(exception, commands.CheckFailure):
            if not isinstance(exception, self.SilentCheckFailure):
                await ctx.send('You can\'t do that.')
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.UserInputError):
            error = ' '.join(exception.args)
            error_data = re.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', error)
            if not error_data:
                await ctx.send('Error: {}'.format(' '.join(exception.args)))
            else:
                await ctx.send('Got to say, I *was* expecting `{1}` to be an `{0}`..'.format(*error_data[0]))
        else:
            info = traceback.format_exception(type(exception), exception, exception.__traceback__, chain=False)
            self.logger.error('Unhandled command exception - {}'.format(''.join(info)))
            await self.notify_devs(info, ctx.message)

    async def on_error(self, event_method, *args, **kwargs):
        info = sys.exc_info()
        await self.notify_devs(traceback.format_exception(*info, chain=False))

    async def on_ready(self):
        self.logger.info('Connected to Discord')
        self.logger.info('Guilds  : {}'.format(len(self.guilds)))
        self.logger.info('Users   : {}'.format(len(set(self.get_all_members()))))
        self.logger.info('Channels: {}'.format(len(list(self.get_all_channels()))))

    async def close(self):
        self.session.close()
        self.database.close()
        await super().close()

    def run(self):
        debug = any('debug' in arg.lower() for arg in sys.argv) or self.config.get('debug_mode', False)

        if debug:
            # if debugging is enabled, use the debug subconfiguration (if it exists)
            if 'debug' in self.config:
                self.config = {**self.config, **self.config['debug']}
            self.logger.info('Debug mode active...')
            self.debug = True

        token = self.config['token']
        cogs = self.config.get('cogs', [])
        self.add_check(right_channel)
        
        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                self.logger.exception('Failed to load cog {}.'.format(cog))
            else:
                self.logger.info('Loaded cog {}.'.format(cog))

        self.logger.info('Loaded {} cogs'.format(len(self.cogs)))

        super().run(token)
