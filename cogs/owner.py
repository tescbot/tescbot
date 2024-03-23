from typing import Literal, Optional

import discord
from discord.ext import commands

from base.cog import BaseCog
from main import Bot


class Owner(BaseCog):
    """Bot owner commands"""

    async def cog_check(self, ctx: commands.Context[Bot]) -> bool:
        # Checks if the user is the owner, or in the owning team, of the bot.
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context[Bot], *, cog_name: str):
        """Loads a cog."""
        try:
            await self.bot.load_extension(cog_name)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context[Bot], *, cog_name: str):
        """Unloads a cog."""
        try:
            await self.bot.unload_extension(cog_name)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.group(name="reload", hidden=True, invoke_without_command=True)
    async def _reload(self, ctx: commands.Context[Bot], *, cog_name: str):
        """Reloads a cog."""
        try:
            await self.bot.reload_extension(cog_name)
        except commands.ExtensionError as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(hidden=True)
    @commands.guild_only()
    async def sync(
        self,
        ctx: commands.Context[Bot],
        guilds: commands.Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """Syncs slash commands."""
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {
                    'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def setup(bot: Bot):
    await bot.add_cog(Owner(bot))
