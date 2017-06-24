import sys
import logging

from discord.ext import commands
import ruamel.yaml as yaml

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class HTSTEMBote(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='sb?')
        self.cfg = {}
        self.debug = False

    def on_command_error(self, context, exception):
        # TODO: notify devs
        pass

    def on_error(self, event_method, *args, **kwargs):
        # TODO: notify devs
        pass

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
        bot.cfg = cfg['debug']
        bot.command_prefix = '..'
    bot.debug = debug

    token = bot.cfg['token']

    for cog in cfg.get('cogs', cogs):
        try:
            bot.load_extension(cog)
        except Exception as e:
            log.exception('Failed to load cog %s', cog)

    bot.run(token)
