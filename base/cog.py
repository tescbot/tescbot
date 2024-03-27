import logging
from typing import Any

from discord.ext import commands

from main import Bot


class BaseCog(commands.Cog):
    """The base cog from which every cog should inherit from."""

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    @property
    def logger(self):
        return logging.getLogger("bot")
