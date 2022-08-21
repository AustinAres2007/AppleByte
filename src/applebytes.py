import discord
import asyncio
from discord.ext import commands, tasks
# Constants

print("Booting")
PREFIX = ">"
BOT_NAME = "AppleByte"
TOKEN = "MTAxMDkxNTc1ODU0MjQyNjE0Mg.GmK2gI.Oh_2tMaLXmivvmHDCxbngh53G7g0xvXXGPXdeU"

intents = discord.Intents.default()
client = commands.AutoShardedBot(PREFIX, intents=intents)

class AppleByteClient(commands.Bot):
    def __init__(self):
        pass

    def on_ready(self):
        pass
    
    async def setup_hook(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}"))
    
async def main():
    await client.start(TOKEN)

asyncio.run(main())