import os
from dotenv import load_dotenv

import discord
from core import Bot


load_dotenv()


def main():
    bot_token = os.getenv("BOT_TOKEN")
    assert bot_token is not None

    bot = Bot(command_prefix="jeremy ", intents=discord.Intents().all())
    bot.setup_logging()
    bot.run(bot_token, log_handler=None)


if __name__ == "__main__":
    main()
