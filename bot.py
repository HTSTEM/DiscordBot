import datetime
import sys
import logging
import traceback

import discord
from discord.ext import commands
import ruamel.yaml as yaml


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class HTSTEMBote(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='sb?')
        self.cfg = {}
        self.debug = False

    async def notify_devs(self, exception_details, msg: discord.Message = None):
        # form embed
        embed = discord.Embed(colour=0xFF0000, title='The bot borked \N{FROWNING FACE WITH OPEN MOUTH}')
        if msg:
            embed.add_field(name='Command', value='```\n{}\n```'.format(msg.content), inline=False)
            embed.set_author(name=msg.author, icon_url=msg.author.avatar_url_as(format='png'))
        embed.set_footer(text='{} UTC'.format(datetime.datetime.utcnow()))
        embed.add_field(name='Error', value='```py\n{}\n```'.format(exception_details), inline=False)

        # loop through all developers, send the embed
        for dev in self.cfg['developers']:
            dev = self.get_user(dev)
            if not dev:
                log.warning('Could not get developer with an ID of %d, skipping.')
                continue
            try:
                await dev.send(embed=embed)
            except discord.Forbidden:
                log.warning('Couldn\'t send error embed to developer %d.', dev.id)

    async def on_message(self, message: discord.Message):
        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        if ctx.command:
            help = 'Run `{}help {}` for help.'.format(ctx.prefix, ctx.command.qualified_name)

        if isinstance(exception, commands.CommandNotFound) or isinstance(exception, commands.CheckFailure):
            # ignore command not found or check failure errors
            pass
        elif isinstance(exception, commands.TooManyArguments):
            await ctx.send('Too many arguments! {}'.format(help))
        elif isinstance(exception, commands.MissingRequiredArgument):
            await ctx.send('You are missing an argument! {} {}'.format(exception, help))
        elif isinstance(exception, commands.DisabledCommand):
            await ctx.send('That command has been disabled.')
        elif isinstance(exception, commands.BadArgument) or isinstance(exception, commands.UserInputError):
            await ctx.send('You got something wrong! {} {}'.format(exception, help))
        else:
            # unwrap
            exception = exception.original if isinstance(exception, commands.CommandInvokeError) else exception
            info = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            await self.notify_devs(info, ctx.message)

    async def on_error(self, event_method, *args, **kwargs):
        info = sys.exc_info()
        await self.notify_devs(''.join(traceback.format_exception(*info)))

cogs = (
    'cogs.core',
    'cogs.misc',
    'cogs.internet',
    'cogs.information',
    'cogs.youtube',
    'cogs.hashing',
)


def load_config():
    with open('config.yml') as f:
        return yaml.load(f, Loader=yaml.Loader)


if __name__ == '__main__':
    bot = HTSTEMBote()

    # load configuration
    cfg = load_config()
    bot.cfg = cfg

    # debug?
    debug = any('debug' in arg.lower() for arg in sys.argv) or cfg.get('debug_mode', False)
    if debug:
        log.info('Debugging mode activated.')
        # use the subconfiguration inside of debug
        new_config = cfg['debug']
        new_config.update(bot.cfg)
        try:
            # delete things that shouldn't be in the new configuration
            del new_config['debug']
            del new_config['debug_mode']
        except (KeyError, AttributeError):
            pass
        print(new_config)
        bot.cfg = new_config
        bot.command_prefix = '..'
    bot.debug = debug

    token = bot.cfg['token']

    for cog in cfg.get('cogs', cogs):
        try:
            bot.load_extension(cog)
        except Exception as e:
            log.exception('Failed to load cog %s', cog)

    bot.run(token)
