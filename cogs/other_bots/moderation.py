import asyncio
import time
import uuid

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

        self.memelordings = [
            # (member, time, started, reason, uuid)
        ]
        self.bannedusers = {}
        self.moderator_role = None
        self.memelord_role = None

        htc = self.bot.get_guild(HTC)
        if htc is not None:
            self.moderator_role = discord.utils.get(htc.roles, id=MODERATOR_ROLE)
            self.memelord_role = discord.utils.get(htc.roles, id=MEMELORD_ROLE)

    async def on_ready(self):
        htc = self.bot.get_guild(HTC)
        if self.moderator_role is None:
            self.moderator_role = discord.utils.get(htc.roles, id=MODERATOR_ROLE)
        if self.memelord_role is None:
            self.memelord_role = discord.utils.get(htc.roles, id=MEMELORD_ROLE)

    async def on_member_ban(self, guild, member):
        self.bannedusers[guild.id] = member.id

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
    async def memelord(self, ctx, member: commands.MemberConverter, length: int, *, reason: str=''):
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
            await ctx.send(f'{member}\'s pumishment has been extended to {length} minutes.')
        else:
            await ctx.send(f'{member} has been memelorded for {length} minutes.')

        m_channel = self.bot.get_guild(HTC).get_channel(MEMELORD_CHANNEL)
        await m_channel.send(member.mention)  # Ping 'em

        # WAIT FOR MESSAGE
        def check(m):
            return m.channel.id == MEMELORD_CHANNEL and m.author.id == member.id
        await self.bot.wait_for('message', check=check)
        if this_meme not in self.memelordings: return

        msg = f'{member.mention}, you have been memelorded for {length} minutes'
        if reason:
            msg += f' because:\n{reason}'
        else:
            msg += '.'
        await m_channel.send(msg)

        await asyncio.sleep(length * 60)
        member = ctx.guild.get_member(member.id)
        # Has it been overwritten or has the member left?
        if this_meme not in self.memelordings or member is None: return

        # REMOVE ROLE
        if self.memelord_role in member.roles:
            await member.remove_roles(self.memelord_role)

        await m_channel.send(f'{member} was released.')


def setup(bot):
    bot.add_cog(Moderation(bot))
