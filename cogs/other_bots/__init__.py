from . import archive, bfb, colors, flairs, joinbot, rules, spoilers, starbot

def setup(bot):
    archive.setup(bot)
    bfb.setup(bot)
    colors.setup(bot)
    flairs.setup(bot)
    joinbot.setup(bot)
    rules.setup(bot)
    spoilers.setup(bot)
    starbot.setup(bot)
