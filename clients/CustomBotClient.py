from discord.ext import commands


class CustomBotClient(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.queue = {}
        self.history = {}

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

        # init each servers queue
        for server in self.guilds:
            self.queue[server.id] = []
            self.history[server.id] = []

    async def on_guild_join(self, guild):
        # add the server to dict for queue and history
        self.queue[guild.id] = []
        self.history[guild.id] = []
