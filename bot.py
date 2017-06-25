import os
import shutil

from cogs.util.bot import HTSTEMBote


def main():
    bot = HTSTEMBote()

    if not os.path.exists('config.yml'):
        shutil.copy('config.example.yml', 'config.yml')

    bot.run()


if __name__ == '__main__':
    main()
