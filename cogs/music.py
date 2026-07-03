import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue : list[dict] = []
        self.text_channel: discord.TextChannel | None = None

    @app_commands.command(name="join", description="makes the bot join your vc")
    async def join(self, interaction: discord.Interaction): 
        if interaction.user.voice is None:
            await interaction.response.send_message("you have to be in a vc")
            return
        
        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is not None:
            await voice_client.move_to(channel)
            await interaction.response.send_message(f"moved to {channel.name}")
            return

        await channel.connect()
        await interaction.response.send_message(f"joined {channel.name}")

    @app_commands.command(name="leave", description="disconnect the bot from vc")
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            await interaction.response.send_message("the bot has to be in vc")
            return
        
        self.queue.clear()
        await voice_client.disconnect()
        await interaction.response.send_message("left the vc")

    YDL_OPTIONS = { "format": "bestaudio/best", "noplaylist": True, "quiet": True, }
    FFMPEG_OPTIONS = { "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn", }

    @app_commands.command(name="play", description="play a song from youtube")
    async def play(self, interaction: discord.Interaction, song: str):
        if interaction.user.voice is None:
            await interaction.response.send_message("you have to be in a vc")
            return
        
        await interaction.response.defer()
        self.text_channel = interaction.channel

        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await interaction.user.voice.channel.connect()

        query = song if song.startswith("http") else f"ytsearch:{song}"

        def extract():
            with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(query, download=False)
                return info["entries"][0] if "entries" in info else info

        track = await asyncio.to_thread(extract)
        url = track["url"]
        title = track["title"]
        self.queue.append({"url": url, "title": title})

        if voice_client.is_playing() or voice_client.is_paused():
            await interaction.followup.send(f"added to queue:  {title}")
        else:
            await interaction.followup.send(f"now playing: {title}")
            await self.start_playing(voice_client)

    async def start_playing(self, voice_client: discord.VoiceClient):
        if not self.queue:
            return
        
        song = self.queue[0]
        source = discord.FFmpegPCMAudio(song["url"], **self.FFMPEG_OPTIONS)

        def after_playing(error):
            if error:
                print(f"error while playing: {error}")
            if self.queue:
                self.queue.pop(0)
            coro = self.play_next(voice_client)
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        
        voice_client.play(source, after=after_playing)
    
    async def play_next(self, voice_client: discord.VoiceClient):
        if self.queue:
            await self.start_playing(voice_client)
            if self.text_channel:
                await self.text_channel.send(f"now playing: {self.queue[0]["title"]}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))