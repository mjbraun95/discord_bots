import openai
import discord
from discord.ext import commands

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

# GPT-4
@bot.command()
async def ask4(ctx, *, question):
    # Call OpenAI's API to generate a response
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question},
                    # {"role": "user", "content": "Who won the world series in 2020?"},
                    # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                    # {"role": "user", "content": "Where was it played?"}
                ]
    )

    # Send the response back to the channel
    await ctx.send(response.choices[0].text)

# TODO: Prompt then ask
@bot.command()
async def prompt(ctx, *, prompt):
    # Call OpenAI's API to generate a response
    response = openai.Completion.create(
        engine='davinci',
        prompt=prompt,
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

if __name__ == '__main__':
    # Acquire bot token
    with open('bot_token.txt', 'r') as f:
        bot_token = f.read().strip()

    with open('api_key.txt', 'r') as f:
        api_key = f.read().strip()
        # Set up OpenAI API credentials
        openai.api_key = api_key

    # Run the bot
    bot.run(bot_token)

