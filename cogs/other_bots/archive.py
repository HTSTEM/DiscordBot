import asyncio
import io
import os

import discord

from ruamel import yaml


debug = 0

if debug == 0:
    TARGET_GUILDS = {
        'HTC': 184755239952318464,
        'HTSTEM': 282219466589208576,
    }
    MIRROR_GUILDS = {
        TARGET_GUILDS['HTC']: [347626231342170112],
        TARGET_GUILDS['HTSTEM']: [379387045400936448],
    }
    #TARGET_GUILD = 184755239952318464
    #MIRROR_GUILDS = [347626231342170112, 379054999524868096]
elif debug == 1:
    TARGET_GUILD = 297811083308171264
    MIRROR_GUILDS = [379054999524868096]


class Archiver:
    def __init__(self, bot):
        super().__init__()

        self.bot = bot

        if not os.path.exists('map.yml'):
            with open('map.yml', 'w') as f:
                f.write('{}')

        with open('map.yml') as f:
            self.lookup = yaml.safe_load(f)

    async def wh(self, webhook, message, file=None, t=0):
        try:
            await webhook.send(
                content=message.content.replace('@', '@\u200b'),
                username=message.author.name,
                avatar_url=message.author.avatar_url,
                tts=False,
                file=file,
                embeds=message.embeds,
            )
        except discord.errors.HTTPException as e:
            if t < 3:
                await asyncio.sleep(0.5)
                await self.wh(webhook, message, file, t + 1)
            else:
                raise e

    async def archive_message(self, guild, message):
        nc = None
        if message.channel.id in self.lookup:
            nc = guild.get_channel(self.lookup[message.channel.id])

            if nc is not None and nc.name != message.channel.name:
                await nc.edit(name=message.channel.name)

        if nc is None:
            nc = await guild.create_text_channel(message.channel.name)
            self.lookup[message.channel.id] = nc.id

            with open('map.yml', 'w') as f:
                yaml.dump(self.lookup, f)

        webhooks = await nc.webhooks()
        if not webhooks:
            webhook = await nc.create_webhook(name='Archiver')
        else:
            webhook = webhooks[0]

        files = []
        for a in message.attachments:
            file = io.BytesIO()
            await a.save(file)
            file.seek(0)
            files.append(discord.File(file, filename=a.filename))

        if not files:
            await self.wh(webhook, message)
        else:
            await self.wh(webhook, message, files[0])
            for file in files[1:]:
                await webhook.send(
                    username=message.author.name,
                    avatar_url=message.author.avatar_url,
                    file=file,
                )

    async def on_message(self, message):
        if message.guild is not None and message.guild.id in MIRROR_GUILDS:
            for gid in MIRROR_GUILDS[message.guild.id]:
                mirror = self.bot.get_guild(gid)
                if mirror:
                    try:
                        await self.archive_message(mirror, message)
                    except discord.Forbidden:
                        pass


def setup(bot):
    bot.add_cog(Archiver(bot))
