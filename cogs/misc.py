import asyncio
import base64
import random
import time
import math

from discord.ext import commands
import discord

from .util.checks import is_developer, right_channel

guild_id = 184755239952318464


class Misc:

    @staticmethod
    async def __local_check(ctx):
        return right_channel(ctx)

    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.send_reminders())

    @staticmethod
    def format_args(cmd):
        params = list(cmd.clean_params.items())
        p_str = ''
        for p in params:
            print(p[1], p[1].default, p[1].empty)
            if p[1].default == p[1].empty:
                p_str += f' <{p[0]}>'
            else:
                p_str += f' [{p[0]}]'

        return p_str

    def format_commands(self, prefix, cmd, name=None):
        cmd_args = self.format_args(cmd)
        if not name:
            name = cmd.name
        name = name.replace('  ', ' ')
        d = f'`{prefix}{name}{cmd_args}`\n'

        if type(cmd) == commands.core.Group:
            cmds = sorted(list(cmd.commands), key=lambda x: x.name)
            for subcmd in cmds:
                d += self.format_commands(prefix, subcmd, name=f'{name} {subcmd.name}')

        return d

    def get_help(self, ctx, cmd, name=None):
        d = f'Help for command `{cmd.name}`:\n'
        d += '\n**Usage:**\n'

        d += self.format_commands(ctx.prefix, cmd, name=name)

        d += '\n**Description:**\n'
        d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

        if cmd.aliases:
            d += '\n**Aliases:**'
            for alias in cmd.aliases:
                d += f'\n`{ctx.prefix}{alias}`'

            d += '\n'

        return d

    async def send_reminders(self):
        await self.bot.wait_until_ready()

        while True:
            current_time = time.time()
            to_remove = []

            dbcur = self.bot.database.cursor()
            
            dbcur.execute("""SELECT memo, user_id, length, start_time FROM memos""")
            for response in dbcur.fetchall():
                if response[2] + response[3] < current_time:
                    user = self.bot.get_user(response[1])
                    if user is not None:
                        await user.send(
                            f'You asked me to remind you to `{base64.b64decode(response[0]).decode("utf-8")}`!'
                        )
                    to_remove.append(response)
            
            dbcur.close()
            
            dbcur = self.bot.database.cursor()
            for r in to_remove:
                try:
                    dbcur.execute("""DELETE FROM memos WHERE user_id = {} AND start_time = {}; """.format(r[1], r[3]))
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            dbcur.close()
            self.bot.database.commit()
            
            await asyncio.sleep(5)
        
    @commands.command(aliases=['memo'])
    async def remind(self, ctx, remind_in, *, to_remind):
        """Sets a reminder.
        remind_in takes the form of <time><unit> where unit is h, m or s.
        For example, 15m would be 15 minutes.
        """
    
        # Bodge to detect if the command is being run from a non-bot channel
        verbose = True
        
        channel_ids = ctx.bot.config.get('ids', {})
        allowed = channel_ids.get('allowed_channels', None)
        blocked = channel_ids.get('blocked_channels', [])
        
        if allowed is not None:
            if ctx.channel.id not in allowed:
                    verbose = False

        if ctx.channel.id in blocked:
            verbose = False        
    
        if len(remind_in) < 2:
            if verbose:
                await ctx.send('Invalid timeframe')
            return

        rem_in = remind_in[:-1]
        unit = remind_in[-1].lower()
        try:
            rem_in = int(rem_in)
        except ValueError:
            if verbose:
                await ctx.send('`{0}` doesn\'t look like a number to me..'.format(rem_in.replace('@', '@\u200b')))
            return
        if unit not in ['h', 'm', 's']:
            if verbose:
                await ctx.send('Unit must be `h`, `m` or `s`')
            return
        
        if unit == 's':
            length = rem_in
        elif unit == 'm':
            length = rem_in * 60
        elif unit == 'h':
            length = rem_in * 60 * 60
        
        if length > 8760 * 60 * 60:
            if verbose:
                await ctx.send('You can\'t set a memo for longer than one year. Sorry for that.')
            else:
                await ctx.author.send('You can\'t set a memo for longer than one year. Sorry for that.')
            return
        elif length < 0:
            if verbose:
                await ctx.send('Yeah.. No.')
            else:
                await ctx.send('Yeah.. No.')
            return
        
        if len(to_remind.replace('@', '@\u200b')) > 1500:
            if verbose:
                await ctx.send('Did it really need to be that long? *Denied*')
            else:
                await ctx.author.send('Did it really need to be that long? *Denied*')
            return
        
        dbcur = ctx.bot.database.cursor()
        dbcur.execute(
            """INSERT INTO memos(memo, user_id, length, start_time) VALUES (?, ?, ?, ?)""",
            (base64.b64encode(to_remind.encode('utf-8')), ctx.author.id, length, int(time.time()))
        )
        dbcur.close()
        ctx.bot.database.commit()
        
        if verbose:
            await ctx.send('Reminder to `{0}` set in {1}{2}!'.format(to_remind.replace('@', '@\u200b'), rem_in, unit))
        else:
            await ctx.author.send(
                f'Reminder to `{0}` set in {1}{2}!'.format(to_remind.replace('@', '@\u200b'), rem_in, unit)
            )

    @commands.command()
    @is_developer()
    async def clear_memos_db(self, ctx):
        await ctx.send(':warning: Clearing DB!')
        
        dbcur = ctx.bot.database.cursor()
        dbcur.execute("""DROP TABLE memos""")
        dbcur.execute("""CREATE TABLE memos(memo TEXT, user_id INTEGER, length INTEGER, start_time INTEGER)""")
        
        dbcur.close()
        ctx.bot.database.commit()
        
        await ctx.send('Done!')
    
    @commands.command()
    async def patroncheck(self, ctx):
        """Checks for uses with the Bot Supporter role on HTC"""
        htc = self.bot.get_guild(guild_id)
        roles = htc.roles
        patreonrole = discord.utils.get(roles, name="BotSupporter")
        patrons = set()
        for user in htc.users:
            if patreonrole in user.roles:
                patrons.add(user)
        await ctx.send({}).format(patrons)

    @commands.command()
    async def roll(self, ctx, sides: int, how_many_dice: int = 1):
        """Rolls a dice."""
        if sides < 1 or how_many_dice < 1:
            return await ctx.send('Yeah, sorry, but you can\'t roll something that doesn\'t exist.')

        if sides > 100 and how_many_dice > 1:
            return await ctx.send('Woahh, that\'s a lot of sides. Try lowering it below 100?')
        elif how_many_dice > 30:
            return await ctx.send('Woahh, that\'s a lot of dice to roll. Try lowering it below 30?')

        if sides == 1:
            return await ctx.send('All {} of the 1-sided dice shocking rolled a 1.'.format(how_many_dice))

        # easter eggs
        if sides == 666:
            return await ctx.send('Satan rolled a nice {} for you.'.format(random.randint(1, sides)))
        elif sides == 1337:
            return await ctx.send('Th3 {}-51d3d d13 r0ll3d 4 {}.'.format(sides, random.randint(1, sides)))
        elif isinstance(ctx.channel, discord.abc.GuildChannel) and sides == ctx.guild.member_count:
            members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
            rolled = random.randint(0, len(members) - 1)
            chosen = members[rolled]
            return await ctx.send('{}? That\'s how many users are on the server! Well, your die rolled a {}, '
                                  'and according to the cache, that member is `{}`.'.format(sides, rolled + 1,
                                                                                            chosen.name))
        result = ', '.join(str(random.randint(1, sides)) for _ in range(how_many_dice))

        die_message = 'The {} {}-sided {} rolled {}.'.format(
            how_many_dice, sides, 'die' if how_many_dice == 1 else 'dice', result)

        # :blobrolleyes: wooningc
        if len(die_message) > 2000:
            return await ctx.send("Congratulations, you've managed to roll a die that we can't send.")

        await ctx.send(die_message)  

    @commands.command()
    async def isprime(self, ctx, num: int):
        """Very simple prime number checker. Implements a slightly-optimized trial division"""
        if num < 1:
            return await ctx.send(f"Don't be silly, {num} can't be prime or composite.")
        if num == 1:
            return await ctx.send(
                'Ooh. Is 1 a prime? Some people say it is, some say it isn\'t, most people don\'t care... is it? ' +
                'Hmm? That\'s up to you to decide.')
        if num in [2, 3, 5, 7]:
            return await ctx.send(f"Yes, {num} is prime. What did you expect me to say?")
        if num % 2 == 0:
            return await ctx.send(f'Why would you think {num}, an even number that isn\'t 2, would be prime?')
        if num % 5 == 0: 
            return await ctx.send(f'Composite. {num} literally ends in a 5...')
        if num > 1e+12:  # Arbitrary limit, adjust as necessary
            return await ctx.send('I may be fast but I\'m not that fast. Try something below 1 trillion.')
        a = 3
        while a <= math.sqrt(num):
            if num % a == 0:
                return await ctx.send('Composite. {0} mod {1} equals 0.'.format(num, a))
            a = a + (2, 4)[a % 10 == 3]  # Skips 5s and even numbers
        return await ctx.send('Prime! {} is only divisible by 1 and itself.'.format(num))

    @commands.command()
    async def help(self, ctx, *args):
        """This help message"""
        if len(args) == 0:
            cats = [cog for cog in self.bot.cogs if self.bot.get_cog_commands(cog)]
            cats.sort()
            width = max([len(cat) for cat in cats]) + 2
            d = '**Categories:**\n'
            for cat in zip(cats[0::2], cats[1::2]):
                d += '**`{}`**{}**`{}`**\n'.format(cat[0], ' ' * int(2.3 * (width - len(cat[0]))), cat[1])
            if len(cats) % 2 == 1:
                d += '**`{}`**\n'.format(cats[-1])

            d += '\nUse `{0}help <category>` to list commands in a category.\n'.format(ctx.prefix)
            d += 'Use `{0}help <command>` to get in depth help for a command.\n'.format(ctx.prefix)

        elif len(args) == 1:
            cats = {cog.lower(): cog for cog in self.bot.cogs if self.bot.get_cog_commands(cog)}
            if args[0].lower() in cats:
                cog_name = cats[args[0].lower()]
                d = 'Commands in category **`{}`**:\n'.format(cog_name)
                cmds = self.bot.get_cog_commands(cog_name)
                for cmd in sorted(list(cmds), key=lambda x: x.name):
                    d += '\n  `{}{}`'.format(ctx.prefix, cmd.name)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is not None:
                        d += ' - {}'.format(brief)
                d += '\n'
            else:
                if args[0] not in ctx.bot.all_commands:
                    d = 'Command not found.'
                else:
                    cmd = ctx.bot.all_commands[args[0]]
                    d = self.get_help(ctx, cmd)
        else:
            d = ''
            cmd = ctx.bot
            cmd_name = ''
            for i in args:
                i = i.replace('@', '@\u200b')
                if cmd == ctx.bot and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                elif type(cmd) == commands.Group and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                else:
                    if cmd == ctx.bot:
                        d += 'Command not found.'
                    else:
                        d += 'Command not found.'
                    break

            else:
                d = self.get_help(ctx, cmd, name=cmd_name)

        # d += '\n*Made by hanss314#0128*'
        return await ctx.send(d)


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Misc(bot))
