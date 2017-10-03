import asyncio
import base64
import random
import time
from math import sqrt

from discord.ext import commands
import discord

from cogs.util import checks


class Misc:
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.send_reminders())

    async def send_reminders(self):
        await self.bot.wait_until_ready()

        while True:
            current_time = time.time()
            to_remove = []

            dbcur = self.bot.database.cursor()
            
            dbcur.execute('''SELECT memo, user_id, length, start_time FROM memos''')
            for response in dbcur.fetchall():
                if response[2] + response[3] < current_time:
                    user = self.bot.get_user(response[1])
                    if user is not None:
                        await user.send('You asked me to remind you to `{0}`!'.format(base64.b64decode(response[0]).decode('utf-8')))
                    to_remove.append(response)
            
            dbcur.close()
            
            dbcur = self.bot.database.cursor()
            for r in to_remove:
                try:
                    dbcur.execute('''DELETE FROM memos WHERE user_id = {} AND start_time = {}; '''.format(r[1], r[3]))
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            dbcur.close()
            self.bot.database.commit()
            
            await asyncio.sleep(5)
        
    @commands.command(aliases=['memo'])
    async def remind(self, ctx, remind_in, *, to_remind):
        '''Sets a reminder.
        remind_in takes the form of <time><unit> where unit is h, m or s.
        For example, 15m would be 15 minutes.
        '''
    
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
        dbcur.execute('''INSERT INTO memos(memo, user_id, length, start_time)
                         VALUES (?, ?, ?, ?)''', (base64.b64encode(to_remind.encode('utf-8')), ctx.author.id, length, int(time.time())))
        dbcur.close()
        ctx.bot.database.commit()
        
        if verbose:
            await ctx.send('Reminder to `{0}` set in {1}{2}!'.format(to_remind.replace('@', '@\u200b'), rem_in, unit))
        else:
            await ctx.author.send('Reminder to `{0}` set in {1}{2}!'.format(to_remind.replace('@', '@\u200b'), rem_in, unit))

    @commands.command()
    @checks.is_developer()
    async def clear_memos_db(self, ctx):
        await ctx.send(':warning: Clearing DB!')
        
        dbcur = ctx.bot.database.cursor()
        dbcur.execute('''DROP TABLE memos''')
        dbcur.execute('''CREATE TABLE memos(memo TEXT, user_id INTEGER, length INTEGER, start_time INTEGER)''')
        
        dbcur.close()
        ctx.bot.database.commit()
        
        await ctx.send('Done!')
    
    @commands.command()
    async def roll(self, ctx, sides: int, how_many_dice: int = 1):
        '''Rolls a dice.'''
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
        """Very simple prime number checker. Limit is 1000000"""
        if num in [2, 3, 5, 7]:
            return await ctx.send("*sigh* Yes, {} is prime.".format(num))
        if num % 2 == 0:
            return await ctx.send('Why would you think {}, an even number, is prime!?'.format(num))
        if num % 5 == 0: 
            return await ctx.send('Composite. {} literally ends in a 5...'.format(num))
        if num >= 1000000:
            return await ctx.send('I may be fast but I\'m not that fast. Try something below 1000000.')
        a = 3
        while a <= sqrt(num):
            if num % a == 0:
                return await ctx.send('Composite. {0} mod {1} equals 0.'.format(num, a))
            a = a + (2, 4)[a % 10 == 3]
        return await ctx.send('Prime! {} is only divisible by 1 and itself'.format(num))


def setup(bot):
    bot.add_cog(Misc(bot))
