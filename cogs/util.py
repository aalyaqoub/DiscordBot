import discord
from discord.ext import commands


class Util(discord.ext.commands.Cog, name='Util module'):
    def __init__(self, bot):
        self.bot = bot

    @discord.ext.commands.command(name="what")
    async def what(self, ctx):
        await ctx.send(f'Yaseen is humar')

    @discord.ext.commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandNotFound):
            await ctx.send('I do not know that command?!')

    @discord.ext.commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Welcome message to new members
        :param member: the new member
        :return: None
        """
        channel = member.guild.system_channel
        print(channel)
        if channel is not None:
            await channel.send(f'Welcome {member.mention} do you want me to sing for you!')