import os
import shutil

from cogs.util.bot import HTSTEMBote


def main():
    bot = HTSTEMBote()
    print(bot.command_prefix)
    bot.run()


if __name__ == '__main__':
    main()
