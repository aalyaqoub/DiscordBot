import discord
import openai
from discord.ext import commands


class ChatGPT(discord.ext.commands.Cog, name='ChatGPT'):
    def __init__(self, bot, openai_api, assistant_style):
        print('hooooo')
        self.bot = bot
        self.openai_api = openai_api
        openai.api_key = openai_api
        self.threads = {}
        self.system_content = assistant_style
        self.system_dict = {"role": "system", "content": self.system_content}

    @discord.ext.commands.command(name="chat")
    async def chat(self, ctx, thread_name):
        channel = ctx.channel
        thread = await channel.create_thread(
            name=thread_name,
            # type=ChannelType.public_thread
        )
        author = ctx.author
        # message = ctx.message
        await thread.send(f"Hello {author.mention}, I am Qita. How can I help you?")

    @discord.ext.commands.Cog.listener("on_message")
    async def on_thread_message(self, message):
        channel = message.channel
        try:
            if type(channel) is discord.threads.Thread:
                if message.author.name != 'qita':
                    if channel in self.threads:
                        message_author = "assistant" if message.author.name == 'qita' else 'user'
                        message_dict = {"role": message_author, "content": message.content}
                        self.threads[channel].append(message_dict)
                    else:
                        # get messages
                        thread_messages = []
                        async for message in channel.history():
                            message_author = "assistant" if message.author.name == 'qita' else 'user'
                            message_dict = {"role": message_author, "content": message.content}
                            thread_messages.append(message_dict)
                            # print(f'message: {message.content}')

                        # reverse order and exclude welcome message from bot
                        thread_messages = thread_messages[len(thread_messages) - 2::-1]
                        thread_messages.insert(0, self.system_dict)

                        # add to threads
                        self.threads[channel] = thread_messages

                    if len(self.threads[channel]) > 0:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=self.threads[channel]
                        )

                        response_text = response.choices[0].message.content
                        response = {"role": 'assistant', "content": response_text}
                        self.threads[channel].append(response)

                        # split response into chunks of 2000 characters to avoid discord character limit
                        chunk_size = 2000
                        text_chunks = [response_text[i:i + chunk_size] for i in range(0, len(response_text), chunk_size)]

                        for text_chunk in text_chunks:
                            # send response to discord
                            await channel.send(text_chunk)

        except Exception as e:
            await channel.send(f'An error occurred.\n{e}\nPlease try again.')
