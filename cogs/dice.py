from random import randint
import discord
from discord.ext import commands

from base.cog import BaseCog
from main import Bot


class Dice(BaseCog):
    """dice commands"""

    @commands.command()
    async def roll(self, ctx: commands.Context[Bot]):
        """regular dice roll"""
        await ctx.send(randint(1,6))

    @commands.command()
    async def rolln(self, ctx: commands.Context[Bot], *, message: str):
        numbers = message.split(",")
        """can specify numbers"""
        await ctx.send(randint(int(numbers[0]), int(numbers[-1])))
        # picking the last number is sort of an error prevention incase people put more than two numbers in

    @commands.command()
    async def pick(self, ctx: commands.Context[Bot]):
        """will pick a random person in the same voice chat as you"""
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("You must join a voice channel first.")
            return
        
        members = voice_channel.members

        randomIndex = randint(0, len(members))
        await ctx.send("I pick => " + str(members[randomIndex]))



async def setup(bot: Bot):
    await bot.add_cog(Dice(bot))

