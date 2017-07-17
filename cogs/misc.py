import asyncio
import random
import time

from discord.ext import commands
import discord


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
                        await user.send('You asked me to remind you to `{0}`!'.format(response[0]))
                    to_remove.append(response)
            
            dbcur.close()
            
            dbcur = self.bot.database.cursor()
            for r in to_remove:
                dbcur.execute('''DELETE FROM memos WHERE memo = '{}' AND user_id = '{}' AND length = '{}' AND start_time = '{}'; '''.format(*r))
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
        
        if length > 72 * 60 * 60:
            if verbose:
                await ctx.send('You can\'t set a memo for more than 72 hours. Sorry for that.')
            else:
                await ctx.author.send('You can\'t set a memo for more than 72 hours. Sorry for that.')
            return
        
        dbcur = ctx.bot.database.cursor()
        dbcur.execute('''INSERT INTO memos(memo, user_id, length, start_time)
                         VALUES (?, ?, ?, ?)''', (to_remind, ctx.author.id, length, time.time()))
        dbcur.close()
        ctx.bot.database.commit()
        
        if verbose:
            await ctx.send('Reminer to `{0}` set in {1}{2}!'.format(to_remind.replace('@', '@\u200b'), rem_in, unit))
        else:
            await ctx.author.send('Reminer to `{0}` set in {1}{2}!'.format(to_remind.replace('@', '@\u200b'), rem_in, unit))

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
        result = ', '.join(str(random.randint(1, sides)) for i in range(how_many_dice))
        await ctx.send('The {} {}-sided {} rolled {}.'.format(how_many_dice, sides, 'die' if how_many_dice == 1 else 'dice', result))


def setup(bot):
    bot.add_cog(Misc(bot))
