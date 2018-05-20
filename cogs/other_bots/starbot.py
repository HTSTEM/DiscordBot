import sqlite3
import re

from discord.ext import commands
import discord


STAR_EMOJI_DEFAULT = ['\N{WHITE MEDIUM STAR}']
STARBOARD_THRESHOLD_DEFAULT = 3


class StarBot:
    INVITE_REGEX = re.compile(r'\bhttps:\/\/discord\.gg\/(\w{1,8})\b')

    def __init__(self, bot):
        self.bot = bot

        self.config = bot.config['starbot']

        self.database = sqlite3.connect("state_cache/htstars.sqlite")
        cursor = self.database.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS stars
                          (original_id INTEGER,
                           starboard_id INTEGER,
                           guild_id INTEGER,
                           author INTEGER,
                           message_content TEXT)""")
        self.database.commit()
        cursor.close()

    @staticmethod
    def star_emoji(stars):
        if 5 > stars >= 0:
            return '\N{WHITE MEDIUM STAR}'
        elif 10 > stars >= 5:
            return '\N{GLOWING STAR}'
        elif 25 > stars >= 10:
            return '\N{DIZZY SYMBOL}'
        else:
            return '\N{SPARKLES}'

    @staticmethod
    def star_gradient_colour(stars):
        p = stars / 13
        if p > 1.0:
            p = 1.0

        red = 255
        green = int((194 * p) + (253 * (1 - p)))
        blue = int((12 * p) + (247 * (1 - p)))
        return (red << 16) + (green << 8) + blue

    def get_emoji_message(self, message, stars):
        emoji = self.star_emoji(stars)

        if stars > 1:
            content = f'{emoji} **{stars}** {message.channel.mention} ID: {message.id}'
        else:
            content = f'{emoji} {message.channel.mention} ID: {message.id}'

        embed = discord.Embed(description=message.content)
        if message.embeds:
            data = message.embeds[0]
            if data.type == 'image':
                embed.set_image(url=data.url)

        if message.attachments:
            file_ = message.attachments[0]
            if file_.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif')):
                embed.set_image(url=file_.url)
            else:
                embed.add_field(
                    name='Attachment',
                    value=f'[{file_.filename}]({file_.url})', inline=False)

        embed.set_author(name=message.author.display_name,
                         icon_url=message.author.avatar_url_as(format='png'))
        embed.timestamp = message.created_at
        embed.colour = self.star_gradient_colour(stars)
        return content, embed

    async def on_message_delete(self, message):
        if message.guild is not None and message.guild.id in self.config.get('starboards', {}):
            board = self.config.get('starboards').get(message.guild.id).get('channel')

            cursor = self.database.cursor()
            cursor.execute("""SELECT * FROM stars
                              WHERE original_id=?""", (message.id,))
            res = cursor.fetchall()

            for i in res:
                try:
                    message = await message.guild.get_channel(board).get_message(i[1])

                    await message.delete()
                except discord.errors.NotFound:
                    pass

                cursor.execute("""DELETE FROM stars
                                  WHERE original_id=?""", (message.id,))
                self.database.commit()

    async def on_raw_reaction_add(self, emoji, message_id, channel_id, user_id):
        chan = self.bot.get_channel(channel_id)
        if chan.guild is not None and chan.guild.id in self.config.get('starboards', {}):
            if emoji.name in self.config.get('stars', STAR_EMOJI_DEFAULT):
                message = await chan.get_message(message_id)
                if user_id == message.author.id:
                    try: await message.remove_reaction(emoji, message.author)
                    except discord.Forbidden: pass
                    return

                if self.INVITE_REGEX.findall(message.content):
                    try: await message.remove_reaction(emoji, message.author)
                    except discord.Forbidden: pass
                    return

                await self.action(message_id, channel_id, user_id)

    async def on_raw_reaction_clear(self, message_id, channel_id):
        chan = self.bot.get_channel(channel_id)
        if chan.guild is not None and chan.guild.id in self.config.get('starboards', {}):
            board = self.config.get('starboards').get(chan.guild.id).get('channel')

            cursor = self.database.cursor()
            cursor.execute("""SELECT * FROM stars
                              WHERE original_id=?""", (message_id,))
            res = cursor.fetchall()

            for i in res:
                try:
                    message = await chan.guild.get_channel(board).get_message(i[1])

                    await message.delete()
                except discord.errors.NotFound:
                    pass

                cursor.execute("""DELETE FROM stars
                                  WHERE original_id=?""", (message_id,))
                self.database.commit()

    async def on_raw_reaction_remove(self, emoji, message_id, channel_id, user_id):
        chan = self.bot.get_channel(channel_id)
        if chan.guild is not None and chan.guild.id in self.config.get('starboards', {}):
            if emoji.name in self.config.get('stars', STAR_EMOJI_DEFAULT):
                await self.action(message_id, channel_id, user_id)

    async def action(self, message_id, channel_id, user_id):
        target_message = await self.bot.get_channel(channel_id).get_message(message_id)
        board = self.config.get('starboards').get(target_message.guild.id).get('channel')
        thresh = self.config.get('starboards').get(target_message.guild.id).get('threshold', STARBOARD_THRESHOLD_DEFAULT)

        if self.INVITE_REGEX.findall(target_message):
            return

        count = 0
        for i in target_message.reactions:
            if i.emoji in self.config.get('stars', STAR_EMOJI_DEFAULT):
                count += i.count

        channel = self.bot.get_channel(board)

        cursor = self.database.cursor()
        cursor.execute("""SELECT * FROM stars
                          WHERE original_id=?""", (message_id,))
        res = cursor.fetchall()

        if res:
            try:
                message = await channel.get_message(res[0][1])

                if count >= thresh:
                    content, embed = self.get_emoji_message(target_message, count)

                    await message.edit(content=content, embed=embed)
                else:
                    await message.delete()
            except discord.errors.NotFound:
                cursor.execute("""DELETE FROM stars
                                  WHERE original_id=?""", (message_id,))
                self.database.commit()
                res = []

        if not res:
            if channel_id != board:
                if count >= thresh:
                    content, embed = self.get_emoji_message(target_message, count)
                    message = await channel.send(content, embed=embed)

                    cursor.execute("""INSERT INTO stars (original_id,
                                                         starboard_id,
                                                         guild_id,
                                                         author,
                                                         message_content)
                                      VALUES (?, ?, ?, ?, ?)""",
                                      (message_id,
                                       message.id,
                                       channel.guild.id,
                                       target_message.author.id,
                                       target_message.content))
                    self.database.commit()
                    cursor.close()


def setup(bot):
    bot.add_cog(StarBot(bot))
