import logging
from typing import Any

from discord.ext import commands

from main import Bot

class BaseCog(commands.Cog):
    """Your base cog. Set vars here which you might use in every cog."""

    def __init__(self, bot: Bot, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot

    @property
    def logger(self):
        return logging.getLogger("Bot")