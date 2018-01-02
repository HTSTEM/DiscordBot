import asyncio
import json
import time

import discord
from slackclient import SlackClient


class ExtendedSlackClient(SlackClient):
    REFRESH_RATE = 0.1
    CACHE_USERS_FOR = 60
    CACHE_CHANNELS_FOR = 60

    def __init__(self, bot):
        self.bot = bot

        with open('config/slack/slack_token.txt') as f:
            tok = self._strip_token(f)
            self.sc = SlackClient(tok)

            self.sc.rtm_connect(with_team_state=False)

        with open('config/slack/hooks.json') as f:
            self.webhooks = json.load(f)
        with open('config/slack/dc_map.json') as f:
            self.dc_map = json.load(f)

        self.loop_running = False

        self.users = {}
        self.channels = {}

    def _reload_channels(self):
        res = self.sc.api_call(
            'conversations.list',
            types='public_channel,private_channel')
        for chan in res['channels']:
            self.channels[chan['id']] = chan['name']

    def get_channel_info(self, channelid):
        if not self.channels:
            self._reload_channels()

        return self.channels[channelid]

    def get_user_info(self, userid):
        refresh = userid not in self.users
        if not refresh:
            if time.time() - self.users[userid][0] > self.CACHE_USERS_FOR:
                refresh = True

        if refresh:
            res = self.sc.api_call(
                'users.info',
                user=userid)

            prof = res['user']['profile']
            name = prof['display_name'] or prof['real_name']
            avatar = prof['image_original']

            self.users[userid] = (time.time(), (name, avatar))

        return self.users[userid][1]

    def _strip_token(self, file_):
        return file_.read().split('\n')[0]

    async def run(self):
        if self.loop_running: return
        self.loop_running = True

        while True:
            for event in self.sc.rtm_read():
                if event.get('type') == 'message':
                    await self.handle_slack_message(event)
            await asyncio.sleep(self.REFRESH_RATE)

    async def handle_slack_message(self, message):
        channel = self.get_channel_info(message.get('channel'))

        if channel not in self.webhooks:
            return
        if message.get('subtype') is not None:
            return
        if message.get('hidden') in ['true', True]:
            return

        username, avatar = self.get_user_info(message.get('user'))
        await self.bot.session.post(self.webhooks[channel],
            json={
                'content': message.get('text'),
                'username': f'{username} (Slack)',
                'avatar_url': avatar
            })

    def handle_discord_message(self, message):
        if not int(message.author.discriminator): return

        if str(message.channel.id) not in self.dc_map:
            return

        if not self.channels:
            self._reload_channels()

        slack_chan = next(key for key, value in self.channels.items() if value == self.dc_map[str(message.channel.id)])

        self.sc.api_call(
            'chat.postMessage',
            as_user='false',
            username=message.author.name,
            icon_url=message.author.avatar_url_as(format='png', size=256),
            channel=slack_chan,
            text=message.content)


class SlackIntergration:
    def __init__(self, bot):
        super().__init__()
        self.slack = ExtendedSlackClient(bot)
        self.bot = bot

        self.bot.loop.create_task(self.slack.run())

    async def on_message(self, message):
        self.slack.handle_discord_message(message)


def setup(bot):
    bot.add_cog(SlackIntergration(bot))
