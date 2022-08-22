import imp
import discord
from discord.ext import commands, tasks
from discord.utils import get
class music(commands.Cog):
    def __init__(self, client: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("Music Loaded")
        self.client = client
    
    @discord.app_commands.command(name="join", description="Will join the Voice Channel you are in.")
    async def join_vc(self, ctx: discord.Interaction):
        voice_instance = get(self.client.voice_clients, guild=ctx.guild_id)
        voice_channel = ctx.user.voice.channel

        print("Connecting")

        if voice_channel and not voice_instance.is_connected():
            await voice_channel.connect()
        else:
            await voice_channel.move()

        await ctx.response.send_message("This is a work in progress command :)")

async def setup(client: commands.Bot):
    await client.add_cog(music(client))