import discord
import asyncio
import os
from discord.ext import commands, tasks
# Constants

PREFIX = ">"
BOT_NAME = "AppleByte"
TOKEN = "MTAxMDkxNTc1ODU0MjQyNjE0Mg.GmK2gI.Oh_2tMaLXmivvmHDCxbngh53G7g0xvXXGPXdeU"
PATH = os.getcwd()

intents = discord.Intents.all()

class AppleByteClient(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self):
        print(f"{BOT_NAME} Online")
    
    async def setup_hook(self):
        for file in os.listdir(f"{PATH}/src/cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")

        await self.tree.sync()

async def main():
    async with AppleByteClient(command_prefix=PREFIX, intents=intents) as client:
        await client.start(TOKEN)

asyncio.run(main())