import asyncio
import time
import uuid

from ruamel import yaml

from discord.ext import commands
import discord


MEMELORD_CHANNEL = 334296605349904384
JOINBOT_CHANNEL = 207659596167249920
MODERATOR_ROLE = 191344863038537728
MEMELORD_ROLE = 334301546710040576
HTC = 184755239952318464


class Moderation:
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

        htc = self.bot.get_guild(HTC)
        if htc is not None:
            self.moderator_role = discord.utils.get(htc.roles, id=MODERATOR_ROLE)
            self.memelord_role = discord.utils.get(htc.roles, id=MEMELORD_ROLE)

        self.timer = self.bot.loop.create_task(self.check_timer())

    async def check_timer(self):
        await self.bot.wait_until_ready()
        m_channel = self.bot.get_guild(HTC).get_channel(MEMELORD_CHANNEL)
        while True:
            for memelording in list(self.memelordings):
                if memelording[2] is not None and time.time() > memelording[2]:
                    member = m_channel.guild.get_member(memelording[0])
                    try:
                        if self.memelord_role in member.roles:
                            await member.remove_roles(self.memelord_role)
                    except discord.NotFound:
                        await m_channel.send(f'{member} left')
                    else:
                        await m_channel.send(f'{member} was released.')

                    self.memelordings.remove(memelording)

                await self.save(None)
            await asyncio.sleep(5)

    async def on_ready(self):
        htc = self.bot.get_guild(HTC)
        if self.moderator_role is None:
            self.moderator_role = discord.utils.get(htc.roles, id=MODERATOR_ROLE)
        if self.memelord_role is None:
            self.memelord_role = discord.utils.get(htc.roles, id=MEMELORD_ROLE)

    async def on_message(self, message):
        if message.channel.id == MEMELORD_CHANNEL:
            for memelording in self.memelordings:
                if memelording[2] is None and memelording[0] == message.author.id:
                    length = memelording[1]
                    memelording[2] = time.time() + length
                    reason = memelording[3]
                    msg = f'{message.author.mention}, you have been memelorded for {length} minutes'
                    if reason:
                        msg += f' because:\n{reason}'
                    else:
                        msg += '.'
                    await message.channel.send(msg)

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

    # Commands stuff
    async def __local_check(self, ctx):
        if ctx.guild.id != HTC:
            raise self.bot.SilentCheckFailure

        if ctx.channel.id != MEMELORD_CHANNEL:
            raise self.bot.SilentCheckFailure

        if self.moderator_role not in ctx.author.roles:
            raise self.bot.SilentCheckFailure

        return True

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

        unique_key = uuid.uuid4().hex  # Used just to avoide collisions

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

        # APPLY ROLE
        if self.memelord_role not in member.roles:
            await member.add_roles(self.memelord_role)

        if extended:
            await ctx.send(f'{member}\'s punishment has been extended to {length} minutes.')
        else:
            await ctx.send(f'{member} has been memelorded for {length} minutes.')

        m_channel = self.bot.get_guild(HTC).get_channel(MEMELORD_CHANNEL)
        await m_channel.send(member.mention)  # Ping 'em

    @memelord.after_invoke
    @forget_memelord.after_invoke
    async def save(self, _):
        with open('state_cache/memelords.yml', 'w') as memelord_file:
            yaml.dump(self.memelordings, memelord_file)


def setup(bot):
    bot.add_cog(Moderation(bot))
