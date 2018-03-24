import asyncio
import time
import uuid

from ruamel import yaml

from discord.ext import commands
import discord

from .spoilers import SADAMA_ROLE, VSPOILER_ROLE, SPOILER_ROLE

debug = 0

if debug == 1: # hanss314
    MEMELORD_CHANNEL = 368282610910363648
    JOINBOT_CHANNEL = 368282610910363648
    MODERATOR_ROLE = 297811340486115330
    MEMELORD_ROLE = 383081878481141761
    HTC = 297811083308171264
    MEMES_CHANNEL = 315541099298947073
    MEMES_VC = 348301159573880834
    MUTED_ROLE = 409418244139646982

else: # htc
    MEMELORD_CHANNEL = 334296605349904384
    JOINBOT_CHANNEL = 207659596167249920
    MODERATOR_ROLE = 191344863038537728
    MEMELORD_ROLE = 334301546710040576
    HTC = 184755239952318464
    MEMES_CHANNEL = 334296645833326604
    MEMES_VC = 334321731277684736
    MUTED_ROLE = 388886242458075137

    LOG_CHANNEL = 422185677354958858

cog = None


class Moderation:
    MAX_RATELIMIT = 300

    def __init__(self, bot):
        super().__init__()

        self.bot = bot
        try:
            with open('state_cache/memelords.yml', 'r') as memelord_file:
                self.memelordings = yaml.load(memelord_file)
        except FileNotFoundError:
            self.memelordings = [
                # [member id, time, ending, reason, uuid]
            ]

        self.bannedusers = {}
        self.moderator_role = None
        self.memelord_role = None
        self.muted_role = None

        htc = self.bot.get_guild(HTC)
        if htc is not None:
            self.moderator_role = discord.utils.get(htc.roles, id=MODERATOR_ROLE)
            self.memelord_role = discord.utils.get(htc.roles, id=MEMELORD_ROLE)
            self.muted_role = discord.utils.get(htc.roles, id=MUTED_ROLE)

        self.timer = self.bot.loop.create_task(self.check_timer())
        self.limit = (-1, 0)  # x per y <- (x, y)
        self.message_rates = {}

    async def check_timer(self):
        await self.bot.wait_until_ready()
        m_channel = self.bot.get_guild(HTC).get_channel(MEMELORD_CHANNEL)
        while True:
            for memelording in list(self.memelordings):
                if memelording[2] is not None and time.time() > memelording[2]:
                    member = m_channel.guild.get_member(memelording[0])
                    try:
                        await member.remove_roles(self.memelord_role)
                    except discord.NotFound:
                        await m_channel.send(f'{member} left')
                    except Exception:
                        import traceback
                        traceback.print_exc()
                    else:
                        await m_channel.send(f'{member} was released.')
                    finally:
                        self.memelordings.remove(memelording)

                await self.save(None)
            await asyncio.sleep(5)

    async def on_ready(self):
        htc = self.bot.get_guild(HTC)
        if self.moderator_role is None:
            self.moderator_role = discord.utils.get(htc.roles, id=MODERATOR_ROLE)
        if self.memelord_role is None:
            self.memelord_role = discord.utils.get(htc.roles, id=MEMELORD_ROLE)
        if self.muted_role is None:
            self.muted_role = discord.utils.get(htc.roles, id=MUTED_ROLE)

    async def on_message(self, message):
        if message.channel.id == MEMELORD_CHANNEL:
            for memelording in self.memelordings:
                if memelording[2] is None and memelording[0] == message.author.id:
                    length = memelording[1]
                    memelording[2] = time.time() + (length * 60)
                    reason = memelording[3]
                    msg = f'{message.author.mention}, you have been memelorded for {length} minutes'
                    if reason:
                        msg += f' because:\n{reason}'
                    else:
                        msg += '.'
                    msg += '\nIf you continue to break rules in here, you may be banned immediately.\n' \
                           'If you leave the server during this timeframe, you *will* be banned immediately.'
                    await message.channel.send(msg)
        elif self.limit != (-1, 0) and message.channel.id == MEMES_CHANNEL:
            if message.channel.permissions_for(message.author).manage_messages:
                # Use Manage Messages to test if a member classes as a moderator
                return

            if 'http://' not in message.content and 'https://' not in message.content and\
               'ftp://' not in message.content and not message.attachments:
                return

            try:
                now = time.time()
                for i in list(self.message_rates[message.author.id]):
                    if now - i > self.limit[1]:
                        self.message_rates[message.author.id].remove(i)

                if len(self.message_rates[message.author.id]) > self.limit[0] - 1:
                    await message.delete()
                else:
                    self.message_rates[message.author.id].append(time.time())
            except KeyError:
                self.message_rates[message.author.id] = [time.time()]

    async def on_message_edit(self, old, message):
        if message.guild is None or message.guild.id != HTC: return
        if old.content == message.content: return
        if message.channel.id == LOG_CHANNEL: return

        channel = self.bot.get_guild(HTC).get_channel(LOG_CHANNEL)
        embed = discord.Embed(title=f'Message edited in #{message.channel.name}',
                              colour=0xff7f00,
                              description=message.content,
                              timestamp=old.created_at)
        if old.content:
            embed.add_field(name='Old content:', value=old.content[:1024])
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format='png'))
        await channel.send(embed=embed)

    async def on_message_delete(self, message):
        if message.guild is None or message.guild.id != HTC: return
        if message.channel.id == LOG_CHANNEL: return

        channel = self.bot.get_guild(HTC).get_channel(LOG_CHANNEL)
        embed = discord.Embed(title=f'Message deleted in #{message.channel.name}',
                              colour=0xff0000,
                              description=message.content,
                              timestamp=message.created_at)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format='png'))
        await channel.send(embed=embed)

    async def on_member_ban(self, guild, member):
        self.bannedusers[guild.id] = member.id

    async def on_member_join(self, member):
        for memelording in self.memelordings:
            if member.id == memelording[0]:
                memelording[0] = member.id
                await member.add_roles(self.memelord_role)

    async def on_member_remove(self, member):
        # Wait for the ban event to fire (if at all)
        await asyncio.sleep(0.25)
        if member.guild.id in self.bannedusers and \
         member.id == self.bannedusers[member.guild.id]:
            del self.bannedusers[member.guild.id]
            return


        if self.memelord_role in member.roles:
            channel = self.bot.get_guild(HTC).get_channel(JOINBOT_CHANNEL)
            return await channel.send(
                f':rotating_light::rotating_light: **{member} was a memelord!** :rotating_light::rotating_light:'
            )

        if self.muted_role in member.roles:
            channel = self.bot.get_guild(HTC).get_channel(JOINBOT_CHANNEL)
            return await channel.send(
                f':rotating_light::rotating_light: **{member} was muted!** :rotating_light::rotating_light:'
            )

    # Commands stuff
    async def __local_check(self, ctx):
        if ctx.guild is None or ctx.guild.id != HTC:
            raise self.bot.SilentCheckFailure
        '''
        if ctx.channel.id != MEMELORD_CHANNEL:
            raise self.bot.SilentCheckFailure
        '''
        if self.moderator_role not in ctx.author.roles:
            raise self.bot.SilentCheckFailure

        return True

    @commands.command()
    async def mute(self, ctx, *members: commands.MemberConverter):
        """Mutes members"""
        for member in members:
            await member.add_roles(self.muted_role)

        await ctx.send(f'Muted {", ".join(str(member) for member in members)}.')

    @commands.command()
    async def ratelimit(self, ctx, messages: int=-1, seconds: int=0):
        self.message_rates = {}
        if messages > -1 and seconds > 0:
            if seconds / messages > self.MAX_RATELIMIT:
                return await ctx.send('That is a silly number. Try again with something less silly.')
            self.limit = (messages, seconds)
            await ctx.send(f'Rate limit set to {self.limit[0]} message(s) every {self.limit[1]} second(s).')
        else:
            self.limit = (-1, 0)
            await ctx.send('Rate limit removed')

    @commands.command()
    async def forget_memelord(self, ctx, member: commands.MemberConverter):
        changed = False
        for i in list(self.memelordings):
            if i[0] == member.id:
                self.memelordings.remove(i)
                changed = True

        if changed:
            return await ctx.send(f'{member} has been removed from the local database.')
        return await ctx.send(f'{member} isn\'t *in* the local database.')

    @commands.command()
    async def memelord(self, ctx, member: commands.MemberConverter, length: str, *, reason: str=''):
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
        for i in list(self.memelordings):
            if i[0] == member.id:
                self.memelordings.remove(i)  # Keep only the most recent one
                extended = True
                if i[3]:
                    reason += f'\n{i[3]}'
                if i[2] is None:
                    length += i[1]
                else:
                    ct = time.time()
                    length += round(max(0, i[1] - (ct - i[2])))

        this_meme = [member.id, length, None, reason, unique_key]
        self.memelordings.append(this_meme)

        if member.voice:
            afk = ctx.guild.afk_channel
            await member.move_to(afk, reason='Memelorded')

        for role in member.roles:
            if role.id in [VSPOILER_ROLE, SPOILER_ROLE, SADAMA_ROLE]:
                await member.remove_roles(role, reason='Memelorded')

        # APPLY ROLE
        if self.memelord_role not in member.roles:
            await member.add_roles(self.memelord_role)

        if extended:
            await ctx.send(f'{member}\'s punishment has been extended to {length} minutes.')
        else:
            await ctx.send(f'{member} has been memelorded for {length} minutes.')

        m_channel = self.bot.get_guild(HTC).get_channel(MEMELORD_CHANNEL)
        await m_channel.send(
            f'{member.mention} Please respond in snail time to start the timer or see the reason'
        )  # Ping 'em


    @memelord.after_invoke
    @forget_memelord.after_invoke
    async def save(self, _):
        with open('state_cache/memelords.yml', 'w') as memelord_file:
            yaml.dump(self.memelordings, memelord_file)

    @commands.command(aliases=['cleanvc'])
    async def clean_vc(self, ctx):
        afk = ctx.guild.afk_channel
        if afk is None:
            return await ctx.send('No AFK channel found.')

        vc = ctx.guild.get_channel(MEMES_VC)
        if not isinstance(vc, discord.VoiceChannel):
            return await ctx.send('No VC found.')

        for member in vc.members:
            if member.voice.mute or member.voice.self_mute:
                await member.move_to(afk, reason='Muted member cleaning')

    @commands.command()
    async def hackban(self, ctx, user_id: int, *, reason=''):
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
