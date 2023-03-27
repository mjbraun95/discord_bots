import discord
from discord.ext import commands

# Create a new bot instance with a prefix
bot = commands.Bot(command_prefix='!')

# Define a new command
@bot.command()
async def hello(ctx):
    # Send a message to the channel where the command was received
    await ctx.send('Hello, world!')

# Replace YOUR_BOT_TOKEN with your actual bot token
bot.run('YOUR_BOT_TOKEN')
