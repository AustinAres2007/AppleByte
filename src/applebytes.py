import discord
import asyncio
import os, logging
from discord.ext import commands, tasks
# Constants

PREFIX = ">"
BOT_NAME = "AppleByte"
TOKEN = "MTAxMDkxNTc1ODU0MjQyNjE0Mg.Gte-10.ckmCeWONg1jgAK9ZbtIgGH3CrtbSILTF-QNIro"
PATH = os.getcwd()

intents = discord.Intents.all()

class AppleByteClient(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = {}
        self.cwd = PATH

    async def on_ready(self):
        print(f"{BOT_NAME} Online")
    
    async def setup_hook(self):
        for file in os.listdir(f"{PATH}/src/cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")

        logging.basicConfig(filename=f"{PATH}/src/data/applebyte.log", level=logging.ERROR, format="%(levelname)s %(name)s %(message)s")
        self.logger = logging.getLogger(__name__)

        await self.tree.sync()

async def main():
    async with AppleByteClient(command_prefix=PREFIX, intents=intents) as client:
        await client.start(TOKEN)

print("Directory: ", PATH)
asyncio.run(main())