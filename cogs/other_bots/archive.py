import asyncio
import io
import os

import discord

from ruamel import yaml


debug = 0

if debug == 0:
    MIRROR_GUILDS = {
        184755239952318464: [347626231342170112, 379392460637339650],  # HTC
        282219466589208576: [379387045400936448, 379054999524868096],  # HTSTEM
    }

elif debug == 1:
    MIRROR_GUILDS = {
        297811083308171264: [379392460637339650, 379054999524868096]
    }


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
            if t < 3 and e.status != 400:
                await asyncio.sleep(0.5)
                await self.wh(webhook, message, file, t + 1)
            elif e.status == 400: pass
            else: raise e

    async def archive_message(self, guild, message):
        nc = None
        if message.channel.id in self.lookup:
            if not isinstance(self.lookup[message.channel.id], list):
                self.lookup[message.channel.id] = [self.lookup[message.channel.id]]
                with open('map.yml', 'w') as f:
                    yaml.dump(self.lookup, f)

            for cid in self.lookup[message.channel.id]:
                nc = guild.get_channel(cid)
                if nc is not None: break

            if nc is not None and nc.name != message.channel.name:
                await nc.edit(name=message.channel.name)

        if nc is None:
            nc = await guild.create_text_channel(message.channel.name)
            try:
                self.lookup[message.channel.id].append(nc.id)
            except KeyError:
                self.lookup[message.channel.id] = []

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
