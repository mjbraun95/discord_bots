import openai
import discord
from discord.ext import commands
import requests
import json

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# Create a new bot instance with a prefix and intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Acquire bot token
with open('bot_token.txt', 'r') as f:
    bot_token = f.read().strip()

# Set up OpenAI API credentials
with open('api_key.txt', 'r') as f:
    api_key = f.read().strip()
    openai.api_key = api_key

def generate_chat_completion(messages, model="gpt-4", temperature=1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

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
    messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
                # {"role": "user", "content": "Who won the world series in 2020?"},
                # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                # {"role": "user", "content": "Where was it played?"}
            ]
    # response = generate_chat_completion(messages=messages)
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=messages
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



    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Translate the following English text to French: 'Hello, how are you?'"}
    ]

    response_text = generate_chat_completion(messages)
    # Run the bot
    bot.run(bot_token)

