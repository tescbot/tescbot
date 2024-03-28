from discord.ext import commands
import os

from base.cog import BaseCog
from main import Bot

from steam import Steam as SteamAPI


class Steam(BaseCog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        key = os.getenv("STEAM_API_KEY")
        assert key is not None, "STEAM_API_KEY is not set in your .env file."

        self.steam_api = SteamAPI(key)

    # spaghetti code !!!alert!!! i don't know what i have done,
    # just followed the documentation for a library (python-steam-api 1.2.2) https://pypi.org/project/python-steam-api/
    # TypeError: 'function' object is not subscriptable
    # it is probably my lack of understanding of python
    @commands.command()
    async def steam(self, ctx: commands.Context[Bot], *, game: str):
        gameData = self.steam_api.apps.search_games(game)
        await ctx.send(gameData)


async def setup(bot: Bot):
    await bot.add_cog(Steam(bot))
