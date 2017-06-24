import sys

from discord.ext import commands
import ruamel.yaml as yaml


bot = commands.Bot('sb?')

cogs = [
    'cogs.core'
]


def load_credentials():
    with open('credentials.yml') as f:
        return yaml.load(f, Loader=yaml.Loader)


if __name__ == '__main__':
    debug = any('debug' in arg.lower() for arg in sys.argv)
    credentials = load_credentials()

    if debug:
        bot.command_prefix = '..'
        token = credentials.get('debug_token', credentials['token'])
    else:
        token = credentials['token']

    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(e)  # TODO logging

    bot.run(token)
