import asyncio
import discord
from clients.CustomBotClient import CustomBotClient
from cogs.util import Util
from cogs.youtube import Youtube
from cogs.chatgpt import ChatGPT

intents = discord.Intents.all()
intents.members = True

bot = CustomBotClient(
    command_prefix='$',
    intents=intents
)


async def main():
    openai_api = ''
    chatgpt_style = 'You are an AI assistant.'
    await bot.add_cog(Util(bot))
    await bot.add_cog(Youtube(bot))
    await bot.add_cog(ChatGPT(bot, openai_api, chatgpt_style))


if __name__ == '__main__':
    discord_token = ''
    asyncio.run(main())
    bot.run(discord_token)
