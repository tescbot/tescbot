import asyncio
import discord
from discord.ext import commands

from base.cog import BaseCog
from main import Bot

import os
from openai import OpenAI
from openai import AsyncOpenAI


class GPT(BaseCog):

    @commands.command()
    async def gpt(self, ctx: commands.Context[Bot], *, message: str):
        client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        stream = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        async for chunk in stream:
            ctx.send(chunk.choices[0].delta.content or "", end="")

async def setup(bot: Bot):
    await bot.add_cog(GPT(bot))