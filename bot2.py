import json
import aiohttp
import discord
import openai
from discord.ext import commands

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"


def load_credentials(filename):
    with open(filename, 'r') as f:
        credentials = json.load(f)
    return credentials


def setup_bot(credentials):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix=credentials["command_prefix"], intents=intents)
    openai.api_key = credentials["api_key"]
    return bot


async def generate_chat_completion(messages, model="gpt-4", temperature=1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    async with aiohttp.ClientSession() as session:
        async with session.post(API_ENDPOINT, headers=headers, json=data) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Error {response.status}: {response.text}")

# Bot commands below

async def hello(ctx):
    await ctx.send("Hello, world!")

def register_bot_commands(bot):
    bot.add_command(commands.Command(hello, name="hello"))

if __name__ == '__main__':
    credentials = load_credentials('config.json')
    bot = setup_bot(credentials)

    # Register bot commands
    register_bot_commands(bot)

    # Run the bot
    bot.run(credentials["bot_token"])
