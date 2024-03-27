import os
import asyncio
import logging
from datetime import datetime, UTC

from discord.ext import commands

from .logging import CustomFormatter, CustomTimedRotatingFileHandler
import cogs


class Bot(commands.Bot):
    """The main bot class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger: logging.Logger | None = None

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
                self.logger.error(
                    f"Failed to load extension '{ext}': <{result.__class__.__name__}> {result}"
                )

    def setup_logging(self) -> None:
        """Sets up the bot's logging."""
        # Create a console output for the logger
        console_out = logging.StreamHandler()
        console_out.setLevel(logging.INFO)
        console_out.setFormatter(CustomFormatter(colored=True))

        # Set up the file output for the logger
        os.makedirs("logs", exist_ok=True)
        logfile_out = CustomTimedRotatingFileHandler(
            lambda _: f"logs/{datetime.now(UTC).strftime("%Y-%m-%d")}.log", atTime="midnight"
        )
        logfile_out.setLevel(logging.INFO)
        logfile_out.setFormatter(CustomFormatter())

        # Create the logger and add the outputs
        self.logger = logging.getLogger("bot")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(console_out)
        self.logger.addHandler(logfile_out)

        # Fetch the internal discord.py logger and add our outputs for debugging
        discord_logger = logging.getLogger("discord")
        discord_logger.addHandler(console_out)
        discord_logger.addHandler(logfile_out)
