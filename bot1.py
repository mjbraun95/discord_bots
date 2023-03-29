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

@bot.command()
async def ask(ctx, *, question):
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question},
    ]

    response_text = generate_chat_completion(messages=messages)

    # Send the response back to the channel
    await ctx.send(response_text)

@bot.command()
async def ask3(ctx, *, question):
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question},
    ]

    response_text = generate_chat_completion(messages=messages, model="gpt-3.5-turbo")

    # Send the response back to the channel
    await ctx.send(response_text)

@bot.command()
async def prompt(ctx, *, prompt):
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": prompt},
    ]
    await ctx.send("Prompted. Enter message below:")

    # Wait for the next message from the user
    question_message = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    # Add the user's question to the messages list
    messages.append({"role": "user", "content": question_message.content})

    response_text = generate_chat_completion(messages=messages)

    # Send the response back to the channel
    await ctx.send(response_text)

@bot.command()
async def prompt3(ctx, *, prompt):
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": prompt},
    ]
    await ctx.send("Prompted. Enter message below:")

    # Wait for the next message from the user
    question_message = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    # Add the user's question to the messages list
    messages.append({"role": "user", "content": question_message.content})

    response_text = generate_chat_completion(messages=messages, model="gpt-3.5-turbo")

    # Send the response back to the channel
    await ctx.send(response_text)

@bot.command()
async def hello(ctx):
    # Send a message to the channel where the command was received
    await ctx.send('Hello, world!')

if __name__ == '__main__':
    # Run the bot
    bot.run(bot_token)

