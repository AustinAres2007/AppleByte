import discord, youtubesearchpython, youtube_dl, os, threading
from discord.ext import commands
from discord.utils import get
from functools import partial

"""
            TODO:
                determine if the client and the user are in the same voice channel (Play command)
                Figure out a way of making playlists
"""
youtube_dl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '64',

    }],
}
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
            voice_instance = await voice_channel.connect(reconnect=True)
            responce = f"Connected to {voice_channel.name}"
        else:
            responce = "You're not in a voice channel."

        await ctx.response.send_message(responce)
    
    @discord.app_commands.command(name="play", description="Will play the requested song from the YouTube library.")
    @discord.app_commands.describe(media="Media Title")
    async def play_media(self, ctx: discord.Interaction, media: str):
        
        voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)

        if not voice_instance:
            return await ctx.response.send_message("I'm not in a voice channel.")

        if not media:
            return await ctx.response.send_message("Please provide a link / search term.")

        music_path = f"{self.client.cwd}/src/data/music/{ctx.guild_id}-music.wav"
        local_opts = youtube_dl_opts
        local_opts['outtmpl'] = music_path

        try:
            os.remove(music_path)
        except PermissionError:
            return await ctx.response.send_message("You are already playing audio.")
        except FileNotFoundError:
            pass
        
        def queue_proxy():
            try:
                queue = self.client.queue[ctx.guild_id]
                to_play = queue[0]['link'] if queue else None

                del self.client.queue[ctx.guild_id][0]
                _download_media(to_play)
            except IndexError:
                return

        def _download_media(link):
            if link:
                try:
                    if os.path.isfile(music_path):
                        os.remove(music_path)
                except KeyError:
                    self.client.queue[ctx.guild_id] = []
                finally:
                    with youtube_dl.YoutubeDL(local_opts) as ydl:
                        ydl.download([str(link)])          

                    source = discord.FFmpegOpusAudio(music_path)
                    voice_instance.play(source, after=lambda e: queue_proxy())
        
        search_results = youtubesearchpython.VideosSearch(media, limit=1)
        media_data = search_results.result()["result"][0]
        link = media_data['link']

        await ctx.response.send_message(f'Selected: {media_data["title"]}\nLink: {link}')
        threading.Thread(target=_download_media, args=(link,)).start()

    @discord.app_commands.command(name='queue', description="Queues a song.")
    @discord.app_commands.describe(media="Media Title")
    async def queue_media(self, ctx: discord.Interaction, media: str):
        search_results = youtubesearchpython.VideosSearch(media, limit=1)
        media_data = search_results.result()["result"][0]
        video_data = {
                    "link": media_data['link'],
                    "name": media_data['title']
        }
        try:
            self.client.queue[ctx.guild_id].append(video_data)
        except KeyError:
            self.client.queue[ctx.guild_id] = []
            self.client.queue[ctx.guild_id].append(video_data)


        await ctx.response.send_message(f'Added \n\n"{media_data["title"]}" to the queue. \n({media_data["link"]})')

async def setup(client: commands.Bot):
    await client.add_cog(music(client))