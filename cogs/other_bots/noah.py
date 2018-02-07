import discord


class Hi:
    def __init__(self, bot):
        super().__init__()

        self.bot = bot

    async def on_message(self, message):
        if message.guild is None:
            if 'hi' in message.content.lower():
                c = self.bot.get_channel(364571585081901056)
                e = discord.Embed(description=message.content)
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
                            value=f'[{file_.filename}]({file_.url})',
                            inline=False
                        )
                        
                embed.set_author(name=message.author.display_name,
                                 icon_url=message.author.avatar_url_as(format='png'))
                embed.timestamp = message.created_at


def setup(bot):
    bot.add_cog(Hi(bot))
