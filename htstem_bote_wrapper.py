import importlib
import discord
import globals
import aiohttp

import htstem_bote

bots = []


def reload_bot():
    print("Reloading bot ", end="")
    importlib.reload(globals)
    importlib.reload(htstem_bote)
    bot = htstem_bote.HTSTEM_Bote(client, session, reload_bot)
    bots.remove(bots[0])
    bots.append(bot)
    print("[DONE]")


if __name__ == "__main__":
    client = discord.Client()
    session = aiohttp.ClientSession(loop=client.loop)
    bot = htstem_bote.HTSTEM_Bote(client, session, reload_bot)
    client.loop.create_task(bot.cary_video_checker())

    bots.append(bot)
    

    @client.event
    async def on_message(message):
        await bots[0].on_message(message)

    @client.event
    async def on_ready():
        await bots[0].on_ready()

    client.run(open("bot-token.txt").read().split("\n")[0])
