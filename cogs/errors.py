import discord
from discord import app_commands
from discord.ext import commands

from base import BaseCog
from main import Bot


class Errors(BaseCog):
    """Global Error Handler"""

    def __init__(self, bot: Bot):
        super().__init__(bot)
        self.bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context[Bot],
        error: commands.CommandError,
    ):
        """Handles chat command errors."""
        self.logger.exception(error)
        raise error

    async def on_app_command_error(
        self,
        interaction: discord.Interaction[Bot],
        error: app_commands.AppCommandError,
    ):
        """Handles slash command errors."""
        self.logger.exception(error)

        error_text = "⚠️ There was an error running this command."
        if interaction.response.is_done():
            await interaction.followup.send(error_text, ephemeral=True)
        else:
            await interaction.response.send_message(error_text, ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Errors(bot))
