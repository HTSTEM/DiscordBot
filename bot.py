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
    cfg = load_config()
    bot.cfg = cfg
    debug = any('debug' in arg.lower() for arg in sys.argv) or cfg.get('debug', False)
    bot.debug = debug

    if debug:
        bot.command_prefix = '..'
        token = cfg.get('debug_token') or cfg['token']
    else:
        token = cfg['token']

    for cog in cfg.get('cogs', cogs):
        try:
            bot.load_extension(cog)
        except Exception as e:
            log.exception('Failed to load cog %s', cog)

    bot.run(token)
