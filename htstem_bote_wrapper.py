import importlib
import discord
import globals

import htstem_bote

bots = []


def reload_bot():
    print("Reloading bot ", end="")
    bots.remove(bots[0])
    importlib.reload(globals)
    importlib.reload(htstem_bote)
    bot = htstem_bote.HTSTEM_Bote(client, reload_bot)
    bots.append(bot)
    print("[DONE]")


if __name__ == "__main__":
    client = discord.Client()
    bot = htstem_bote.HTSTEM_Bote(client, reload_bot)
    bots.append(bot)

    @client.event
    async def on_message(message):
        await bots[0].on_message(message)

    @client.event
    async def on_ready():
        await bots[0].on_ready()

    client.run(open("bot-token.txt").read().split("\n")[0])
