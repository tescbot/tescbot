from __future__ import annotations
import shutil
import asyncio
from typing import Optional

import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL

from base.cog import BaseCog
from main import Bot


class Song:
    ytdl = YoutubeDL({"format": "bestaudio/best"})
    ffmpeg = "ffmpeg"
    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn"
    }

    def __init__(self, title: str, source: str, stream_url: str) -> None:
        self.title = title
        self.source = source
        self.stream_url = stream_url

    @classmethod
    def from_query(cls, query: str) -> list[Song]:
        # TODO: Accept playlists
        # TODO: Accept spotify, soundcloud, etc.

        results = VideosSearch(query, limit=1).result()["result"]
        if len(results) > 0:
            result = results[0]
            stream_url = Song.ytdl.extract_info(
                result["link"], download=False)["url"]
            return cls(result["title"], result["link"], stream_url)
        else:
            return None

    def to_audio_source(self) -> discord.AudioSource:
        """Converts the song into a compatible discord audio source."""
        # Check if the executeable exists
        assert shutil.which(Song.ffmpeg) is not None
        # Converts the audio stream into a discord audio source using ffmpeg
        return discord.FFmpegPCMAudio(self.stream_url, executable=Song.ffmpeg, **Song.ffmpeg_options)

    def to_hyperlink(self, embed=True) -> str:
        link = self.source
        if not embed:
            link = f"<{link}>"
        return f"[{self.title}]({link})"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Song):
            return False

        return self.source == __value.source


class Music(BaseCog):
    """Music commands"""

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)

        self.music_queue: list[Song] = []
        self.current_song: Song | None = None

    @property
    def vc(self) -> discord.VoiceClient | None:
        if len(self.bot.voice_clients) > 0:
            return self.bot.voice_clients[0]
        else:
            return None

    async def play_next(self):
        """Plays the next song in the queue."""
        assert self.vc is not None

        if len(self.music_queue) > 0:
            self.current_song = self.music_queue.pop(0)
            self.vc.play(self.current_song.to_audio_source(), after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(), self.bot.loop))

    @commands.command()
    async def join(self, ctx: commands.Context[Bot], voice_channel: Optional[discord.VoiceChannel] = None):
        """Joins your, or the specified, voice channel."""
        if voice_channel is None:
            if ctx.author.voice is None:
                await ctx.send("You must join a voice channel first.")
                return

            voice_channel = ctx.author.voice.channel

        if self.vc is not None and self.vc.is_connected():
            if self.vc.channel == voice_channel:
                await ctx.send("The bot is already in this voice channel.")
                return

            await self.vc.disconnect()

        await voice_channel.connect()
        await ctx.send(f"Joined {voice_channel.mention}")

    @commands.command()
    async def leave(self, ctx: commands.Context[Bot]):
        """Leaves the current voice channel."""
        if self.vc is not None and self.vc.is_connected():
            voice_channel = self.vc.channel
            await self.vc.disconnect()
            await ctx.send(f"Left {voice_channel.mention}")
        else:
            await ctx.send("The bot is not in a voice channel.")

    @commands.command()
    async def search(self, ctx: commands.Context[Bot], *, query: Optional[str]):
        """Searches for a song."""
        song = Song.from_query(query)
        if song is None:
            await ctx.send("Could not find a song matching the query.")
        else:
            await ctx.send(song.to_hyperlink())

    @commands.command()
    async def play(self, ctx: commands.Context[Bot], *, query: Optional[str]):
        """Plays a song."""
        if query is None:
            await ctx.send("You must enter a query.")
            return

        song = Song.from_query(query)
        if song is None:
            await ctx.send("Could not find a song matching the query.")
            return

        self.music_queue.insert(0, song)

        if self.vc is None or not self.vc.is_connected():
            await self.join(ctx)

        self.vc.stop()
        await self.play_next()
        await ctx.send(f"Playing {self.current_song.to_hyperlink()}")

    @commands.command()
    async def skip(self, ctx: commands.Context[Bot]):
        """Skips the current song."""
        if self.vc is None:
            ctx.send(f"The bot is not in a voice channel.")
            return

        self.vc.stop()
        await self.play_next()
        await ctx.send(f"Skipping the current song. Now playing: {
            self.current_song.to_hyperlink()}")

    @commands.command()
    async def pause(self, ctx: commands.Context[Bot]):
        """Pauses the current song."""
        if self.vc is None:
            await ctx.send("The bot is not in a voice channel.")
            return

        if not self.vc.is_playing():
            await ctx.send("The bot is not currently playing anything.")
            return

        if self.vc.is_paused():
            await ctx.send("The bot is already paused.")
            return

        self.vc.pause()
        await ctx.send(f"Paused.")

    @commands.command()
    async def resume(self, ctx: commands.Context[Bot]):
        """Resumes the current song."""
        if self.vc is None:
            await ctx.send("The bot is not in a voice channel.")
            return

        if not self.vc.is_paused():
            await ctx.send("The bot is already resumed")
            return

        self.vc.resume()
        await ctx.send(f"Resumed.")

    @commands.command()
    async def song(self, ctx: commands.Context[Bot]):
        """Gets the currently playing song."""
        if self.vc is None or not self.vc.is_playing():
            await ctx.send("No song is playing.")

        await ctx.send(f"The current song is: {self.current_song.to_hyperlink()}")

    @commands.group()
    async def queue(self, ctx: commands.Context[Bot]):
        """Gets the queue. Also contains the subcommands for adding and removing from the queue"""
        if ctx.invoked_subcommand is None:
            if len(self.music_queue) > 0:
                await ctx.send("\n".join(f"{i+1}. {song.to_hyperlink(False)}" for i, song in enumerate(self.music_queue)))
            else:
                await ctx.send("The queue is empty.")

    @queue.command()
    async def add(self, ctx: commands.Context[Bot], *, query: Optional[str]):
        """Adds a song to the queue."""
        song = Song.from_query(query)
        if song is None:
            await ctx.send("Could not find a song matching the query.")
            return

        self.music_queue.append(song)
        await ctx.send(f"Added {song.to_hyperlink()} to the queue.")

    @queue.command()
    async def remove(self, ctx: commands.Context[Bot], *, query: Optional[str]):
        """Removes a song from the queue."""
        song = Song.from_query(query)
        if song is None:
            await ctx.send("Could not find a song matching the query.")
            return

        try:
            self.music_queue.remove(song)
            await ctx.send(f"Removed {song.to_hyperlink()} from the queue.")
        except ValueError:
            await ctx.send(f"{song.to_hyperlink()} could not be found in the queue.")


async def setup(bot: Bot):
    await bot.add_cog(Music(bot))
