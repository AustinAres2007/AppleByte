from http.client import HTTPException
import discord, youtubesearchpython, youtube_dl, os, threading, asyncio
from discord.ext import commands
from discord.utils import get

"""
            TODO:
                determine if the client and the user are in the same voice channel (Play command)
                Figure out a way of making playlists
"""

errors = {
    "no_vc": "You're not in a voice channel"
}
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
# Main Music cog

class music(commands.Cog):

    # Initialisation

    def __init__(self, client: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("Music Loaded")
        self.client = client
    
    # Joining and Leaving Voice Channel

    @discord.app_commands.command(name="join", description="Will join the Voice Channel you are in.")
    @discord.app_commands.checks.cooldown(1, 15)
    async def join_vc(self, ctx: discord.Interaction):
        try:
            voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)
            voice_channel: discord.VoiceChannel = ctx.user.voice.channel

            if voice_instance and voice_instance.is_connected():
                await voice_instance.move_to(voice_channel)
                responce = f"Moved to {voice_channel.name}"
            elif voice_channel:
                voice_instance = await voice_channel.connect(reconnect=True)
                responce = f"Connected to {voice_channel.name}"

        except AttributeError:
            responce = errors['no_vc']
        finally:
            await ctx.response.send_message(responce)

    @discord.app_commands.command(name="disconnect", description="Disconnects from users voice channel.")
    @discord.app_commands.checks.cooldown(1, 20)
    async def disconnect_vc(self, ctx: discord.Interaction):
        try:
            voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)
            voice_channel: discord.VoiceChannel = ctx.user.voice.channel

            if voice_instance and voice_instance.is_connected():
                await voice_instance.disconnect(force=True)
                response = f"Disconnected from {voice_channel.name}"
            else:
                response = "I am not in a voice channel."
        
        except AttributeError:
            response = errors['no_vc']
        finally:
            await ctx.response.send_message(response)

    # Media audio

    @discord.app_commands.command(name="play", description="Will play the requested song from the YouTube library.", extras={
        discord.ClientException: "Already playing audio.", 
    })
    @discord.app_commands.describe(media="Media Title")
    @discord.app_commands.checks.cooldown(1, 20)
    async def play_media(self, ctx: discord.Interaction, media: str):
        
        voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)

        if not voice_instance:
            return await ctx.response.send_message("I'm not in a voice channel.")

        if not media:
            return await ctx.response.send_message("Please provide a link / search term.")

        if voice_instance.is_playing():
            return await ctx.response.send_message("I am currently playing audio.")
        
        music_path = f"{self.client.cwd}/src/data/music/{ctx.guild_id}-music{PREFERRED_FILEEXTENSION}"
        temp_path = f"{self.client.cwd}/src/data/music/{ctx.guild_id}-temp{PREFERRED_FILEEXTENSION}"

        local_opts = youtube_dl_opts
        local_opts['outtmpl'] = music_path

        try:
            os.remove(music_path)
        except PermissionError:
            return await ctx.response.send_message("You are already playing audio.")
        except FileNotFoundError:
            pass

        def send(message: str):
            asyncio.run_coroutine_threadsafe(ctx.channel.send(message), self.client.loop)
        
        def download_proxy(__link__: str, secondary: bool):
            temp_opts = local_opts

            if secondary:
                temp_opts['outtmpl'] = temp_path
            if os.path.exists(temp_path):
                os.remove(temp_path)

            with youtube_dl.YoutubeDL(temp_opts) as ydl:
                self.client.asy_download[ctx.guild_id] = True
                ydl.download([str(__link__)])
                self.client.asy_download[ctx.guild_id] = False

        def queue_proxy():
            try:
                queue = self.client.queue[ctx.guild_id]
                try:
                    to_play = queue[0]['link'] if queue else None

                    media_data = self.client.queue[ctx.guild_id][0]
                    del self.client.queue[ctx.guild_id][0]
                    _download_media(to_play, media_data, False)
                except IndexError:
                    send("Queue now empty, finished playing.")
            except IndexError:
                return

        def _download_media(link: str, metadata: dict, download_link: bool):
            if link:
                try:
                    if os.path.isfile(music_path):
                        os.remove(music_path)
                except KeyError:
                    self.client.queue[ctx.guild_id] = []
                finally:
                    try:
                        if not download_link:
                            while self.client.asy_download[ctx.guild_id]:
                                continue
                            else:
                                os.rename(temp_path, music_path)
                        else:
                            download_proxy(link, False)

                        send(f'Playing "{metadata["title"]}"')

                        if self.client.queue[ctx.guild_id]:
                            threading.Thread(target=download_proxy, args=(self.client.queue[ctx.guild_id][0]['link'], True,)).start()

                        source = discord.FFmpegOpusAudio(music_path)
                        voice_instance.play(source, after=lambda e: queue_proxy())

                    except youtube_dl.utils.DownloadError:
                        send("Could not download media, please try again.")

        search_results = youtubesearchpython.VideosSearch(media, limit=1)
        media_data = search_results.result()["result"][0]
        link = media_data['link']

        if len(media_data['duration'].split(":")) > 2:
            await ctx.response.send_message("Media cannot be more than an hour long.")
        else:
            await ctx.channel.send(f'Selected: {media_data["title"]}\nLink: {link}\nDownloading..\n')
            threading.Thread(target=_download_media, args=(link, media_data, True,)).start()
    
    @discord.app_commands.command(name='queue', description="Queues a song, or displays the queue if did not pass a keyword.", extras={HTTPException: "Could not send reply."})
    @discord.app_commands.describe(media="Media Title")
    async def queue_media(self, ctx: discord.Interaction, media: str=None):
        try:
            if media is None:
                reply = [f"{x['title']}\nAuthor: {x['channel']['name']}" for x in self.client.queue[ctx.guild_id]]
                if not reply:
                    reply = "No queued songs."
                else:
                    reply = "\n\n".join(reply)

                return await ctx.response.send_message(reply)

            if len(self.client.queue[ctx.guild_id]) > 15:
                return await ctx.response.send_message("Cannot add more than 15 songs in the queue.")

            search_results = youtubesearchpython.VideosSearch(media, limit=1)
            media_data = search_results.result()["result"][0]
            
            if len(media_data['duration'].split(":")) > 2:
                await ctx.response.send_message("You cannot download media more than an hour long.")
            else:
                try:
                    self.client.queue[ctx.guild_id].append(media_data)
                except KeyError:
                    self.client.queue[ctx.guild_id] = []
                    self.client.queue[ctx.guild_id].append(media_data)

            await ctx.response.send_message(f'Added \n\n"{media_data["title"]}" to the queue. \n({media_data["link"]})')
        except KeyError:
            self.client.queue[ctx.guild_id] = []
    
    @discord.app_commands.command(name="clear", description="Pops specified amount of videos off the queue.")
    @discord.app_commands.checks.cooldown(1, 10)
    @discord.app_commands.describe(many="How many songs to clear from queue. Type 0 or leave the prompt empty to clear all.")
    async def clear_queue(self, ctx: discord.Interaction, many: int=0):
        final_response = "Error"
        if many > len(self.client.queue[ctx.guild_id]):
            final_response = "Not enough videos to clear."
        else:
            if not many:
                response = "all"
                self.client.queue[ctx.guild_id].clear()
            else:
                self.client.queue[ctx.guild_id] = self.client.queue[ctx.guild_id][:many]
                response = many

            final_response = f"Popped {response} video(s) off the end of the queue."

        await ctx.response.send_message(final_response)

    # Media control commands

    async def voice_checks(self, ctx, method: str, success_message: str):
        """
        voice_checks

        This function makes the "skip", "pause", and "resume"
        easier to program for. Because they require the same checks, and the only difference is the
        success message and the function call. (Pass message context, the method, and the message to send.)
        """

        reply = "Error"
        try:
            voice_instance: discord.VoiceClient = get(self.client.voice_clients, guild=ctx.guild)
            voice_channel: discord.VoiceChannel = ctx.user.voice.channel

            try:
                if voice_instance and voice_instance.is_connected():
                    getattr(voice_instance, method)()
                    reply = success_message
                else:
                    reply = "I am not in any voice channel"

            except AttributeError:
                reply = "You are not playing any media."

        except AttributeError:
            reply = "You're not in a voice channel."
        finally:
            await ctx.response.send_message(reply)

    @discord.app_commands.command(name='skip', description="Skips media.", extras={AttributeError: "You're not in a voice channel."})
    @discord.app_commands.checks.cooldown(1, 15)
    async def skip_media(self, ctx: discord.Interaction):
        await self.voice_checks(ctx, "stop", "Skipped media.")

    @discord.app_commands.command(name="resume", description="Resumes media.")
    @discord.app_commands.checks.cooldown(1, 10)
    async def resume_media(self, ctx: discord.Interaction):
        await self.voice_checks(ctx, "resume", "Resumed media.")

    @discord.app_commands.command(name="pause", description="Pauses media.")
    @discord.app_commands.checks.cooldown(1, 10)
    async def pause_media(self, ctx: discord.Interaction):
        await self.voice_checks(ctx, "pause", "Paused media.")

async def setup(client: commands.Bot):
    await client.add_cog(music(client))