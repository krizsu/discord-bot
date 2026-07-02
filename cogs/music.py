import discord
from discord import app_commands
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
        
        await voice_client.disconnect()
        await interaction.response.send_message("left the vc")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))