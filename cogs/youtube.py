import discord
from discord.ext import commands
import yt_dlp


class Youtube(discord.ext.commands.Cog, name='Youtube module'):
    def __init__(self, bot):
        self.bot = bot
        self.history = {}

    # play url, queue, add, clear, skip, pause, resume,
    @discord.ext.commands.command(name="play")
    async def play(self, ctx, url: str):
        """
        Play a song from a url
        :param ctx: the context of the command
        :param url: the url of the song
        :return: None
        """
        print(f'The server id is {ctx.guild.id}')
        print(f'The server name is {ctx.guild.name}')

        # init voice client
        voice_client = await self._set_client(ctx)

        # stop playing if already playing
        if voice_client.is_playing():
            await voice_client.stop()

        # play song
        await self._play_song(ctx, url, voice_client)

    @discord.ext.commands.command(name="queue")
    async def queue(self, ctx):
        """
        Queue a song
        :param ctx: the context of the command
        :return: None
        """
        # init server/queue info
        server_id = ctx.message.author.guild.id
        server_queue = self.bot.queue[server_id]
        queue_str = 'The Queue:'

        # return queue info
        if len(server_queue) == 0:
            await ctx.send('The queue is empty')
        else:
            for idx, song_url in enumerate(server_queue):
                song_info = await self._get_info(ctx, song_url)
                queue_str = queue_str + '\n' + str(idx + 1) + ': ' + song_info["title"]
            await ctx.send(queue_str)

    @discord.ext.commands.command(name="add")
    async def add(self, ctx, url: str):
        # add url to the server's queue list
        server_id = ctx.message.author.guild.id
        self.bot.queue[server_id].append(url)

        await ctx.send('Added to queue')

    @discord.ext.commands.command(name="skip")
    async def skip(self, ctx):
        voice_client = await self._set_client(ctx)

        if voice_client.is_playing():
            voice_client.stop()
            # await self._play_queue(ctx, voice_client)
        else:
            await ctx.send('There is nothing to skip')

    @discord.ext.commands.command(name="pause")
    async def pause(self, ctx):
        """
        Pause the current song
        :param ctx: the context of the command
        :return: None
        """
        ctx.voice_client.pause()
        await ctx.send('The song has been paused')

    @discord.ext.commands.command(name="resume")
    async def resume(self, ctx):
        """
        Resume the current song
        :param ctx: the context of the command
        :return: None
        """
        ctx.voice_client.resume()
        await ctx.send('The song has resumed')

    @discord.ext.commands.command(name="clear")
    async def clear(self, ctx):
        """
        Clear the queue
        :param ctx: the context of the command
        :return: None
        """
        # empty the queue of the server
        server_id = ctx.message.author.guild.id
        self.bot.queue[server_id] = []

    @discord.ext.commands.command(name="leave")
    async def leave(self, ctx, guild_id):
        """
        Leave the server
        :param ctx: the context of the command
        :param guild_id: the id of the server to leave
        :return: None
        """
        if ctx.message.author.guild_permissions.administrator:
            if int(ctx.message.author.guild.id) == int(guild_id):
                await ctx.send(f"I'm leaving: {guild_id}")
                await self.bot.get_guild(int(guild_id)).leave()
                print(f'I left server {guild_id}')
            else:
                await ctx.send(f"I can't leave {guild_id} as it is not this server.\n"
                               f"This server's id is {ctx.message.author.guild.id}.")
        else:
            await ctx.send(f"You need to be an admin to make the bot leave the server.")

    @discord.ext.commands.command(name="exit")
    async def exit(self, ctx):
        """
        Exit the bot from VC
        :param ctx: the context of the command
        :return: None
        """
        # get the voice client
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # if connected to a voice channel, disconnect
        if voice_client is not None:
            await voice_client.disconnect()
        else:
            await ctx.send('I am not connected anything.')

    ##UTILS
    async def _get_info(self, ctx, url):
        """
        Get the info of the song
        :param ctx: the context of the command
        :param url: the url of the song
        :return: song_info: the info of the song
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            # get the info of the song using youtube_dl
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(url, download=False)
        except yt_dlp.DownloadError as error:
            await ctx.send(f'Opps {url} is not a valid youtube link')

        return song_info

    async def _set_client(self, ctx):
        """
        Set the voice client
        :param ctx: the context of the command
        :return: the voice client
        """
        # choose what voice channel to join
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if ctx.author.voice.channel is None:
            voice_channel = discord.utils.get(ctx.guild.voice_channels, name='General')
        else:
            # if the bot is already in another channel that is different from the users,
            # disconnect and connect to the user's channel
            voice_channel = ctx.author.voice.channel
            if voice_client is not None and voice_client.channel is not ctx.author.voice.channel:
                await ctx.send(f'Bot will disconnect from {voice_client.channel.name}')
                await voice_client.disconnect()
                voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # if the bot is not connected to any channel, connect to the user's channel
        if voice_client is None:
            await voice_channel.connect()
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        return voice_client

    async def _play_song(self, ctx, url, voice_client):
        """
        Play the song
        :param ctx: the context of the command
        :param url: the url of the song
        :param voice_client: the voice client
        :return: None
        """
        # get song info
        song_info = await self._get_info(ctx, url)

        # convert the youtube audio source into a source discord can use
        audio = song_info["formats"][8]["url"]
        source = discord.FFmpegPCMAudio(audio)

        try:
            await ctx.send(f"Now playing {song_info['title']}")
            voice_client.play(source, after=lambda e: self.bot.loop.create_task(self._play_queue(ctx, voice_client)))

            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 1
        except Exception as ex:
            print('an error happened')
            print(ex)

    async def _play_queue(self, ctx, voice_client):
        """
        Play the next song in the queue
        :param ctx: the context of the command
        :param voice_client: the voice client
        :return: None
        """
        server_id = ctx.message.author.guild.id
        server_queue = self.bot.queue[server_id]

        # play the next thing in the queue
        if len(server_queue) > 0:
            new_url = server_queue.pop()
            await self._play_song(ctx, new_url, voice_client)
