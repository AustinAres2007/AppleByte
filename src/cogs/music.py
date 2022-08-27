from urllib.error import HTTPError
import discord, youtubesearchpython, youtube_dl, os, threading, time, pathlib

from http.client import HTTPException
from turtle import down
from discord.ext import commands
from discord.utils import get
from functools import partial

"""
            TODO:
                determine if the client and the user are in the same voice channel (Play command)
                Figure out a way of making playlists
"""

PREFERRED_FILEEXTENSION = '.mp3'
youtube_dl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64',

    }],
}
class music(commands.Cog):
    def __init__(self, client: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("Music Loaded")
        self.client = client
    
    def play_message(self, message: os.PathLike, guild):
        guild_vc = get(self.client.voice_clients, guild=guild)
        guild_vc.pause()
    @discord.app_commands.command(name="join", description="Will join the Voice Channel you are in.", extras={
        discord.ClientException: "Already in VC."
        })
    @discord.app_commands.checks.cooldown(1, 5)
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
    
    @discord.app_commands.command(name="play", description="Will play the requested song from the YouTube library.", extras={
        discord.ClientException: "Already playing audio.", 
        youtube_dl.utils.DownloadError: "Error downloading media, please retry."
    })
    @discord.app_commands.describe(media="Media Title")
    @discord.app_commands.checks.cooldown(1, 20)
    async def play_media(self, ctx: discord.Interaction, media: str):
        # TODO: test if single songs work, and delete all songs after play command has finished.
        processing = []
        voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)

        if not voice_instance:
            return await ctx.response.send_message("I'm not in a voice channel.")

        if not media:
            return await ctx.response.send_message("Please provide a link / search term.")

        if voice_instance.is_playing():
            return await ctx.response.send_message("I am currently playing audio.")

        base_path = f"{self.client.cwd}/src/data/music/"
        music_path = f"{base_path}{ctx.guild_id}-music{PREFERRED_FILEEXTENSION}"
        local_opts = youtube_dl_opts
        
        def queue_proxy(file: str, _old: str):
            if os.path.isfile(_old):
                        os.remove(_old)
            if file:
                try:

                    _old = file
                    queue = self.client.queue[ctx.guild_id]
                    to_play = queue[0]['link'] if queue else None

                    del self.client.queue[ctx.guild_id][0]
                    return _download_media(to_play, True, f"{base_path}{file}", _old)
                except IndexError:
                    return
            return

        def _download_media(link: str, queue: bool, file_to_play: str, _old: str):
            if link:
                queue_entry = queued_file = None
                try:
                    queue_entry = self.client.queue[ctx.guild_id][0]
                except KeyError:
                    self.client.queue[ctx.guild_id] = []
                except IndexError:
                    pass
        
                def download(d_link: str, filename: str):
                    try:
                        local_opts['outtmpl'] = f"{base_path}{filename}"
                        with youtube_dl.YoutubeDL(local_opts) as ydl:
                            processing.append(filename)
                            ydl.download([d_link])   
                            time.sleep(4)
                            processing.remove(filename)       
                    except (youtube_dl.utils.DownloadError, HTTPError):
                        pass

                if not queue:
                    download(link, f"{ctx.guild_id}-music{PREFERRED_FILEEXTENSION}")
                if queue_entry:
                    queued_file = f"{ctx.guild_id}-{queue_entry['id']}{PREFERRED_FILEEXTENSION}"
                    threading.Thread(target=download, args=(queue_entry['id'],queued_file,)).start()

                while os.path.basename(file_to_play) in processing:
                    pass

                source = discord.FFmpegOpusAudio(file_to_play)
                voice_instance.play(source, after=lambda e: queue_proxy(queued_file, _old,))
        
        search_results = youtubesearchpython.VideosSearch(media, limit=1)
        media_data = search_results.result()["result"][0]
        link = media_data['link']

        await ctx.response.send_message(f'Selected: {media_data["title"]}\nLink: {link}')
        threading.Thread(target=_download_media, args=(link, False, music_path, music_path,)).start()

    @discord.app_commands.command(name='queue', description="Queues a song.", extras={HTTPException: "Could not send reply."})
    @discord.app_commands.describe(media="Media Title")
    async def queue_media(self, ctx: discord.Interaction, media: str):
        search_results = youtubesearchpython.VideosSearch(media, limit=1)
        media_data = search_results.result()["result"][0]
        video_data = {
                    "link": media_data['link'],
                    "name": "-".join(media_data['title'].lower().split(' ')),
                    "id": media_data['id']
        }
        try:
            self.client.queue[ctx.guild_id].append(video_data)
        except KeyError:
            self.client.queue[ctx.guild_id] = []
            self.client.queue[ctx.guild_id].append(video_data)


        await ctx.response.send_message(f'Added \n\n"{media_data["title"]}" to the queue. \n({media_data["link"]})')

async def setup(client: commands.Bot):
    await client.add_cog(music(client))