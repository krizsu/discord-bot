import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ID = int(os.getenv("SERVER_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    guild = discord.Object(SERVER_ID)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synchronized {len(synced)} commands")

async def main():
    async with bot:
        await bot.load_extension("cogs.general")
        await bot.start(TOKEN)

asyncio.run(main())