from discord.ext import commands
import discord

class Listeners(commands.Cog, name="listeners"):
    def __init__(self, client: commands.Bot):
        self.client = client
        print("Listeners Loaded")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.client.queue[guild.id] = []

async def setup(client: commands.Bot):
    await client.add_cog(Listeners(client))