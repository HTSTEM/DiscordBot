import asyncio
import time
import uuid

from ruamel import yaml

from discord.ext import commands
import discord


cog = None

# TODO: YAML
config = {
    290573725366091787: {
        'leave_c': 290757101914030080,
        'leave_r': [320939806530076673],

        'log_c': 319830765842071563,

        'jail': {
            'channel': 365892375492427778,
            'role': 320939806530076673,
            'respond': True,
            'black_roles': [290750253102268427],
            'extra_msg': 'o/'
            }
    },
    184755239952318464: {
        'leave_c': 207659596167249920,  # joinbot
        'leave_r': [
            334301546710040576,  # Memelord
            388886242458075137,  # Muted
        ],

        'log_c':   422185677354958858,  # messagebot

        'jail': {
            'channel': 334296605349904384,  # snail-time
            'role':    334301546710040576,  # Memelord
            'respond': True,
            'black_roles': [
                397130936464048129,  # Spoilers
                392842859931369483,  # Vote spoilser
                392847202575187970,  # SADAMA
            ],
            'extra_msg': 'If you continue to break rules in here, you may be banned immediately.\n'
                         'If you leave the server during this timeframe, you *will* be banned immediately.'
        }
    }
}


class Moderation:
    def __init__(self, bot):
        super().__init__()

        self.bot = bot
        try:
            with open('state_cache/in_jail.yml', 'r') as file_:
                self.in_jail = yaml.load(file_)
        except FileNotFoundError:
            self.in_jail = [
                # [guild, member, time, ending, reason, uuid]
            ]

        self.config = config

        self.banned_users = {}
        self.timer = self.bot.loop.create_task(self.check_timer())

    async def check_timer(self):
        await self.bot.wait_until_ready()

        while True:
            for convict in list(self.in_jail):
                print(convict)
                if convict[3] is not None and time.time() > convict[3]:
                    guild = self.bot.get_guild(convict[0])

                    if guild is None:
                        self.in_jail.remove(convict)
                        print('g')
                        continue

                    member = guild.get_member(convict[1])
                    if member is None:
                        self.in_jail.remove(convict)
                        print('m')
                        continue

                    if guild.id not in self.config or self.config[guild.id].get('jail', {}).get('role') is None:
                        self.in_jail.remove(convict)
                        print('e')
                        continue

                    channel = guild.get_channel(self.config[guild.id]['jail']['channel'])
                    try:
                        await member.remove_roles(discord.Object(self.config[guild.id]['jail']['role']))
                    except Exception as e:
                        if channel:
                            await channel.send(f'Error removing role: {e}')
                    else:
                        if channel:
                            await channel.send(f'{member} was released')

                    self.in_jail.remove(convict)

                    await self.save(None)
            await asyncio.sleep(5)

    async def on_message(self, message):
        if message.guild is None or message.guild.id not in self.config: return
        jail = self.config[message.guild.id].get('jail')
        if not jail: return

        if not jail['respond']: return
        if message.channel.id != jail['channel']: return

        for convict in self.in_jail:
            if convict[0] != message.guild.id or convict[3]: continue
            if convict[1] != message.author.id: continue

            length = convict[2]
            convict[3] = time.time() + (length * 60)
            reason = convict[4]
            
            msg = f'{message.author.mention}, you have been confined for {length} minutes'
            if reason:
                msg += f' because:\n{reason}'
            else:
                msg += '.'
            if 'extra_msg' in jail:
                msg += '\n' + jail['extra_msg']

            await message.channel.send(msg)
            await self.save(None)

    async def on_message_edit(self, old, message):
        if message.guild is None or message.guild.id not in self.config: return
        channel = message.guild.get_channel(self.config[message.guild.id].get('log_c', 0))
        if channel is None: return

        if old.content == message.content: return
        if message.channel.id == channel.id: return

        embed = discord.Embed(title=f'Message edited in #{message.channel.name}',
                              colour=0xff7f00,
                              description=message.content,
                              timestamp=old.created_at)
        if old.content:
            embed.add_field(name='Old content:', value=old.content[:1024])
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format='png'))
        await channel.send(embed=embed)

    async def on_message_delete(self, message):
        if message.guild.id not in self.config: return
        channel = message.guild.get_channel(self.config[message.guild.id].get('log_c', 0))
        if channel is None: return
        
        if message.channel.id == channel.id: return
        
        embed = discord.Embed(title=f'Message deleted in #{message.channel.name}',
                              colour=0xff0000,
                              description=message.content,
                              timestamp=message.created_at)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format='png'))
        await channel.send(embed=embed)

    async def on_member_ban(self, guild, member):
        self.banned_users[guild.id] = member.id

    async def on_member_join(self, member):
        for convict in self.in_jail:
            if member.id == convict[1]:
                if member.guild.id == convict[0]:
                    jail = self.config.get(member.guild.id, {}).get('jail', {})
                    try:
                        await member.add_roles(jail.get('role', 0))
                    except discord.Error:
                        pass

    async def on_member_remove(self, member):
        # Wait for the ban event to fire (if at all)
        await asyncio.sleep(0.25)
        if member.guild.id in self.banned_users and \
         member.id == self.banned_users[member.guild.id]:
            del self.banned_users[member.guild.id]
            return
        
        roles = self.config.get(member.guild.id, {}).get('leave_r', [])
        c_id = self.config.get(member.guild.id, {}).get('leave_c', 0)
        
        channel = member.guild.get_channel(c_id)
        if channel is None: return
        
        for i in member.roles:
            if i.id in roles:
                return await channel.send(
                    f':rotating_light::rotating_light: **{member} left with role {i}!** :rotating_light::rotating_light:'
                )

    # Commands stuff
    async def __local_check(self, ctx):
        if not ctx.channel.permissions_for(ctx.author).kick_members:
            raise self.bot.SilentCheckFailure

        return True

    @commands.command(aliases=['forget_memelord'])
    async def forget_punishment(self, ctx, member: commands.MemberConverter):
        """Retain a user indefinatly"""
        changed = False
        for i in list(self.in_jail):
            if i[0] == member.id:
                self.in_jail.remove(i)
                changed = True

        if changed:
            return await ctx.send(f'{member} has been removed from the local database.')
        return await ctx.send(f'{member} isn\'t *in* the local database.')

    @commands.command(aliases=['memelord'])
    async def punish(self, ctx, member: commands.MemberConverter, length: str, *, reason: str=''):
        """Put someone in jail"""
        unit = length[-1]
        try:
            if unit in '0123456789':
                length = int(length)
            elif unit in ['m', 'h', 'd']:
                if unit == 'm': length = int(length[:-1])
                if unit == 'h': length = int(length[:-1]) * 60
                if unit == 'd': length = int(length[:-1]) * 3600
            else:
                return await ctx.send('Expected the unit to be "m", "h" or "d".')
        except ValueError:
            return await ctx.send('Expected length to be an integer with an optional unit.')

        unique_key = uuid.uuid4().hex  # Used just to avoid collisions

        extended = False
        for i in list(self.in_jail):
            if i[1] == member.id:
                self.in_jail.remove(i)  # Keep only the most recent one
                extended = True
                if i[4]:
                    reason += f'\n{i[3]}'
                if i[3] is None:
                    length += i[1]
                else:
                    ct = time.time()
                    length += round(max(0, i[1] - (ct - i[2]) / 60))

        release_time = None
        jail = self.config.get(ctx.guild.id, {}).get('jail')
        if not jail: return
        if not jail.get('respond'):
            release_time = time.time() + length * 60

        convict = [ctx.guild.id, member.id, length, release_time, reason, unique_key]
        self.in_jail.append(convict)

        if member.voice:
            afk = ctx.guild.afk_channel
            await member.move_to(afk, reason='Send to jail')

        black_roles = jail.get('black_roles')
        for role in ctx.author.roles:
            if role.id in black_roles:
                await member.remove_roles(role, reason='Sent to jail')

        # APPLY ROLE
        try:
            await member.add_roles(discord.Object(jail.get('role', 0)))
        except:
            await ctx.send('Failed to apply role')

        if extended:
            await ctx.send(f'{member}\'s punishment has been extended to {length} minutes.')
        else:
            await ctx.send(f'{member} has been confined for {length} minutes.')

        if jail.get('respond'):
            chan = ctx.guild.get_channel(jail.get('channel'))
            if chan:
                await chan.send(
                    f'{member.mention} Please respond to start the timer and see the reason.'
                )

    @punish.after_invoke
    @forget_punishment.after_invoke
    async def save(self, _):
        with open('state_cache/in_jail.yml', 'w') as file_:
            yaml.dump(self.in_jail, file_)

    @commands.command()
    async def hackban(self, ctx, user_id: int, *, reason=''):
        """Ban a user by ID"""
        user = discord.Object(user_id)
        try:
            await ctx.guild.ban(user, reason=reason)
            await ctx.send(f'Banned <@{user_id}>')
        except discord.Forbidden:
            await ctx.send('I do not have permissions.')
        except discord.HTTPException:
            await ctx.send('Banning failed, did you type the id correctly?')


def setup(bot):
    global cog
    bot.add_cog(Moderation(bot))
    cog = bot.cogs['Moderation']

def teardown(bot):
    global cog
    cog.timer.close()
