import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime, UTC
from typing import Callable

import discord
from discord.ext import commands

import cogs

from dotenv import load_dotenv
load_dotenv()


class Bot(commands.Bot):
    """The main bot class."""

    def __init__(self, *args, logger: logging.Logger, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    async def on_ready(self):
        """Executes when the bot is connected and online."""
        assert self.user is not None
        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def setup_hook(self) -> None:
        """Sets up the bot when it is started."""
        results = await asyncio.gather(
            *(self.load_extension(ext) for ext in cogs.initial_extensions),
            return_exceptions=True,
        )

        for ext, result in zip(cogs.initial_extensions, results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to load extension '{ext}': <{
                                  result.__class__.__name__}> {result}")


def get_logfile_namer(filename_fmt: str) -> Callable[[str], str]:
    """Generates the name of each log file."""
    def namer(prev_filename: str = "") -> str:
        return filename_fmt % {"dt": datetime.now(UTC).strftime("%Y-%m-%d")}
    return namer


async def main():
    bot_token = os.getenv("BOT_TOKEN")
    assert bot_token is not None

    # --- Setup logger
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s")

    # Create a console output for the logger
    console_out = logging.StreamHandler()
    console_out.setLevel(logging.INFO)
    console_out.setFormatter(formatter)
#
    # Set up the file output for the logger
    os.makedirs("logs", exist_ok=True)
    namer = get_logfile_namer("logs/%(dt)s.log")
    logfile_out = TimedRotatingFileHandler(namer(), atTime="midnight")
    logfile_out.namer = namer
    logfile_out.setLevel(logging.INFO)
    logfile_out.setFormatter(formatter)

    # Create the logger and add the outputs
    logger = logging.getLogger("Bot")
    logger.setLevel(logging.INFO)
    logger.addHandler(console_out)
    logger.addHandler(logfile_out)

    # Fetch the internal discord.py logger and add our outputs for debugging
    discord_logger = logging.getLogger("discord")
    discord_logger.addHandler(console_out)
    discord_logger.addHandler(logfile_out)

    # --- Create bot
    bot = Bot(
        command_prefix="jeremy ",
        intents=discord.Intents().all(),
        logger=logger
    )

    # Start the bot
    async with bot:
        await bot.start(bot_token)


if __name__ == "__main__":
    asyncio.run(main())
