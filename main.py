import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime, UTC

import discord
from discord.ext import commands

import cogs

from dotenv import load_dotenv
load_dotenv()


class Bot(commands.Bot):
    def __init__(self, *args, logger: logging.Logger, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    async def on_ready(self):
        assert self.user is not None
        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def setup_hook(self) -> None:
        results = await asyncio.gather(
            *(self.load_extension(ext) for ext in cogs.initial_extensions),
            return_exceptions=True,
        )
        for ext, result in zip(cogs.initial_extensions, results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to load extension '{ext}': <{
                                  result.__class__.__name__}> {result}")


def get_logfile_name(filename_fmt: str) -> str:
    return filename_fmt % {"dt": datetime.now(UTC).strftime("%Y-%m-%d")}


async def main():
    bot_token = os.getenv("BOT_TOKEN")
    assert bot_token is not None

    # Setup logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s")

    console_out = logging.StreamHandler()
    console_out.setLevel(logging.INFO)
    console_out.setFormatter(formatter)

    os.makedirs("logs", exist_ok=True)
    logfile_out = TimedRotatingFileHandler(
        get_logfile_name("logs/%(dt)s.log"), atTime="midnight")
    logfile_out.namer = get_logfile_name
    logfile_out.setLevel(logging.INFO)
    logfile_out.setFormatter(formatter)

    logger = logging.getLogger("Bot")
    logger.setLevel(logging.INFO)
    discord_logger = logging.getLogger("discord")
    logging.getLogger('discord.http').setLevel(logging.INFO)

    logger.addHandler(console_out)
    discord_logger.addHandler(console_out)
    logger.addHandler(logfile_out)
    discord_logger.addHandler(logfile_out)

    # Create bot

    bot = Bot(
        command_prefix="jeremy ",
        intents=discord.Intents().all(),
        logger=logger
    )

    async with bot:
        await bot.start(bot_token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
