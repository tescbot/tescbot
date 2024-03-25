from random import randint, choice
from discord.ext import commands

from base.cog import BaseCog
from main import Bot


class Dice(BaseCog):
    """Dice commands."""

    @commands.command()
    async def roll(self, ctx: commands.Context[Bot], low: int = 1, high: int = 6):
        """Rolls a dice."""
        await ctx.send(randint(low, high))

    @commands.command()
    async def pick(self, ctx: commands.Context[Bot]):
        """Picks a random person from the same voice channel as you."""
        if ctx.author.voice is None:
            await ctx.send("You must join a voice channel first.")
            return

        picked = choice(ctx.author.voice.channel.members)
        await ctx.send(f"I pick {picked.mention}.")


async def setup(bot: Bot):
    await bot.add_cog(Dice(bot))
