import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="checks if the bot is online")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")

async def setup(bot: commands.bot):
    await bot.add_cog(General(bot))