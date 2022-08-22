from re import search
import discord, youtubesearchpython, validators
from discord.ext import commands, tasks
from discord.utils import get

"""
            TODO:
                determine if the client and the user are in the same voice channel (Play command)
                Figure out a way of making playlists
"""

class music(commands.Cog):
    def __init__(self, client: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("Music Loaded")
        self.client = client
    
    @discord.app_commands.command(name="join", description="Will join the Voice Channel you are in.")
    async def join_vc(self, ctx: discord.Interaction):
        voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)
        voice_channel: discord.VoiceChannel = ctx.user.voice.channel

        if voice_instance and voice_instance.is_connected():
            await voice_instance.move_to(voice_channel)
            responce = f"Moved to {voice_channel.name}"
        elif voice_channel:
            voice_instance = await voice_channel.connect()
            responce = f"Connected to {voice_channel.name}"
        else:
            responce = "You're not in a voice channel."

        await ctx.response.send_message(responce)
    
    @discord.app_commands.command(name="play", description="Will play the requested song from the YouTube library.")
    @discord.app_commands.describe(media="URL or Video Title")
    async def play_media(self, ctx: discord.Interaction, media: str):
        if not media:
            return await ctx.response.send_message("Please provide a link / search term.")

        voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)
        voice_channel: discord.VoiceProtocol = ctx.user.voice

        # Joins VC if bot is not in one.
        if not (voice_instance and voice_instance.is_connected()):
            if voice_channel:
                await voice_channel.channel.connect()
            else:
                return await ctx.response.send_message("You're not in a voice channel.")
        
        if validators.url(media):
            pass
        else:
            search_results = youtubesearchpython.VideosSearch(media, limit=1)
            media_url = search_results.result()["result"][0]
        
        await ctx.response.send_message(f'Selected: {media_url["title"]}\nLink: {media_url["link"]}')

        

            
            


async def setup(client: commands.Bot):
    await client.add_cog(music(client))