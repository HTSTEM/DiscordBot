import traceback
import datetime
import logging
import sys

from discord.ext import commands
import ruamel.yaml as yaml
import discord
import aiohttp


class HTSTEMBote(commands.AutoShardedBot):
    # Move subclass to different file
    def __init__(self, log_file=None, *args, **kwargs):
        self.debug = False
        self.config = {}
        with open('config.yml', 'r') as f:
            self.config = yaml.load(f, Loader=yaml.Loader)

        logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s] %(message)s')
        self.logger = logging.getLogger('bot')

        super().__init__(command_prefix='sb?', *args, **kwargs)

    async def on_message(self, message):
        channel_ids = self.config.get('ids', {})

        allowed = channel_ids.get('allowed_channels', None)
        blocked = channel_ids.get('blocked_channels', [])

        if allowed is not None:
            if message.channel.id not in allowed:
                return

        if message.channel.id in blocked:
            return

        await self.process_commands(message)

    async def notify_devs(self, lines, message: discord.Message = None):
        # form embed
        embed = discord.Embed(colour=0xFF0000, title='Error occurred \N{FROWNING FACE WITH OPEN MOUTH}')

        if message is not None:
            if len(message.content) > 400:
                async with aiohttp.ClientSession() as sess:
                    async with sess.post('https://hastebin.com/documents', data=message.content.encode(),
                                         headers={'content-type': 'application/json'}) as resp:
                        json = await resp.json()
                        embed.add_field(name='Command', value='https://hastebin.com/{}.py'.format(json['key']), inline=False)
            else:
                embed.add_field(name='Command', value='```\n{}\n```'.format(message.content), inline=False)
            embed.set_author(name=message.author, icon_url=message.author.avatar_url_as(format='png'))

        embed.set_footer(text='{} UTC'.format(datetime.datetime.utcnow()))

        error_message = ''.join(lines)
        if len(error_message) > 1000:
            async with aiohttp.ClientSession() as sess:
                async with sess.post('https://hastebin.com/documents', data=error_message.encode(),
                                     headers={'content-type': 'application/json'}) as resp:
                    json = await resp.json()
                    embed.add_field(name='Error', value='https://hastebin.com/{}.py'.format(json['key']), inline=False)
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
            lines = traceback.format_exception(type(exception),
                                               exception.__cause__,
                                               exception.__cause__.__traceback__)
            self.logger.error(''.join(lines))
            await self.notify_devs(lines, ctx.message)
            return

        if isinstance(exception, commands.CheckFailure):
            await ctx.send('Check failed: {}'.format(' '.join(exception.args)))

        elif isinstance(exception, commands.MissingRequiredArgument):
            await ctx.send('Error: {}'.format(' '.join(exception.args)))

        elif isinstance(exception, commands.UserInputError):
            await ctx.send('Error: {}'.format(' '.join(exception.args)))

        elif isinstance(exception, discord.Forbidden):
            try:
                await ctx.send('Error: {}'.format(' '.join(exception.args)))
            except:
                pass
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

    def run(self):
        debug = any('debug' in arg.lower() for arg in sys.argv) or self.config.get('debug', False)

        if debug:
            token = self.config.get('debug_token', self.config['token'])
            self.logger.info('Debug mode active...')
            self.logger.level = logbook.debug
            self.debug = True
        else:
            token = self.config['token']

        cogs = self.config.get('cogs', [])

        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                self.logger.exception('Failed to load cog {}.'.format(cog))
            else:
                self.logger.info('Loaded cog {}.'.format(cog))

        self.logger.info('Loaded {} cogs'.format(len(self.cogs)))

        super().run(token)
