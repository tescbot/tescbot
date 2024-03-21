from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from base.cog import BaseCog
from main import Bot

class Errors(BaseCog):
    """Global Error Handler"""

    def __init__(self, bot: Bot):
        super().__init__(bot)
        self.bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: Any,
        error: commands.CommandError,
    ):
        """Handle prefix command errors here."""
        self.logger.exception(error)
        raise error

    async def on_app_command_error(
        self,
        interaction: discord.Interaction[Bot],
        error: app_commands.AppCommandError,
    ):
        """Handle slash command errors here."""
        self.logger.exception(error)

        error_text: str = error.__class__.__name__
        if interaction.response.is_done():
            await interaction.followup.send(error_text, ephemeral=True)
        else:
            await interaction.response.send_message(error_text, ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Errors(bot))