import discord
import asyncio
from discord.ext import commands, tasks
# Constants

PREFIX = ">"
BOT_NAME = "AppleByte"
TOKEN = "MTAxMDkxNTc1ODU0MjQyNjE0Mg.GmK2gI.Oh_2tMaLXmivvmHDCxbngh53G7g0xvXXGPXdeU"

intents = discord.Intents.all()
client = commands.AutoShardedBot(PREFIX, intents=intents)

class AppleByteClient(commands.Bot):
    def __init__(self)
async def main():
    await client.start(TOKEN)

asyncio.run(main())