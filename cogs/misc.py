from discord.ext import commands

from base import BaseCog
from main import Bot


class Misc(BaseCog):
    """Misc commands"""

    @commands.command()
    async def say(self, ctx: commands.Context[Bot], *, message: str):
        await ctx.send(message)


async def setup(bot: Bot):
    await bot.add_cog(Misc(bot))
