import openai
import discord
from discord.ext import commands

# Set up OpenAI API credentials
openai.api_key = 'YOUR_API_KEY'

# Create a new bot instance with a prefix and intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Define a new command to generate AI responses
@bot.command()
async def ask(ctx, *, question):
    # Call OpenAI's API to generate a response
    response = openai.Completion.create(
        engine='davinci',
        prompt=question,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.5
    )

    # Send the response back to the channel
    await ctx.send(response.choices[0].text)

# Define a new command
@bot.command()
async def hello(ctx):
    # Send a message to the channel where the command was received
    await ctx.send('Hello, world!')

# Acquire bot token
with open('bot_token.txt', 'r') as f:
    bot_token = f.read().strip()

# Run the bot
bot.run(bot_token)

