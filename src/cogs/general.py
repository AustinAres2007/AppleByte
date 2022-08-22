from code import interact
import discord
from discord.ext import commands, tasks

class general(commands.Cog):
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("General Loaded")
        self.client: commands.Bot = client

    @discord.app_commands.command(name="test", description="Check if Client is online.")
    async def online(self, ctx: discord.Interaction):
        print("Test command working")
        await ctx.response.send_message("Online")

    @discord.app_commands.command(name="stop", description="Shuts down bot client")
    @commands.is_owner()
    async def halt(self, ctx: discord.Interaction):
        await ctx.response.send_message("Shutting down.")
        await self.client.close()

async def setup(client):
    await client.add_cog(general(client))