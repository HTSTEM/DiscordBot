from discord.ext import commands


def is_staff():
    def predicate(ctx: commands.Context) -> bool:
        return ctx.author.permissions_in(ctx.guild.default_channel).manage_messages
    return commands.check(predicate)


def is_developer():
    def predicate(ctx: commands.Context) -> bool:
        in_config = ctx.author.id in ctx.bot.cfg['developers']
        has_role = ctx.bot.cfg['developer_role_id'] in map(lambda r: r.id, ctx.author.roles)
        return in_config or has_role
    return commands.check(predicate)
