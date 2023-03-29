from discord.ext import commands
import aiohttp
import discord
import openai

import json
import requests

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

# TODO: Change these functions below + implement switchmodels command

async def ask(ctx, *, question):
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question},
    ]

    response_text = await generate_chat_completion(messages=messages)

    # Send the response back to the channel
    await ctx.send(response_text)


async def ask3(ctx, *, question):
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question},
    ]

    response_text = await generate_chat_completion(messages=messages, model="gpt-3.5-turbo")

    # Send the response back to the channel
    await ctx.send(response_text)


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

    response_text = await generate_chat_completion(messages=messages)

    # Send the response back to the channel
    await ctx.send(response_text)


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

    response_text = await generate_chat_completion(messages=messages, model="gpt-3.5-turbo")

    # Send the response back to the channel
    await ctx.send(response_text)

async def send_long_message(ctx, content, max_length=2000):
    if len(content) <= max_length:
        await ctx.send(content)
    else:
        while len(content) > max_length:
            await ctx.send(content[:max_length])
            content = content[max_length:]
        await ctx.send(content)

# TODO: Add a prompt list command

async def choose_prompt(ctx):
    # TODO: Expand
    prompts = [
        "You are a helpful assistant.",
        "You are an expert on movies.",
        "You are a history buff.",
        "You are a travel advisor.",
    ]

    # Send the list of prompts to the channel
    prompt_list = "\n".join([f"{i+1}. {prompt}" for i, prompt in enumerate(prompts)])
    await ctx.send(f"Please choose a prompt by entering its number:\n{prompt_list}")

    # Wait for the user to select a prompt
    def check_prompt_choice(m):
        return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= len(prompts)



    chosen_prompt_msg = await bot.wait_for('message', check=check_prompt_choice)
    chosen_prompt_index = int(chosen_prompt_msg.content) - 1
    chosen_prompt = prompts[chosen_prompt_index]

    # Ask the user for their question
    await ctx.send("Please enter your question:")

    # Wait for the user's question
    question_message = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": chosen_prompt},
        {"role": "user", "content": question_message.content},
    ]

    response_text = await generate_chat_completion(messages=messages)

    # Send the response back to the channel
    await send_long_message(ctx, response_text)



async def hello(ctx):
    # Send a message to the channel where the command was received
    await ctx.send('Hello, world!')

# Don't forget to include the new command in your main function, if needed.
def register_bot_commands(bot):
    bot.add_command(commands.Command(ask, name="ask"))
    bot.add_command(commands.Command(ask3, name="ask3"))
    bot.add_command(commands.Command(prompt, name="prompt"))
    bot.add_command(commands.Command(prompt3, name="prompt3"))
    bot.add_command(commands.Command(choose_prompt, name="choose"))
    bot.add_command(commands.Command(hello, name="hello"))

if __name__ == '__main__':
    credentials = load_credentials('config.json')
    bot = setup_bot(credentials)

    # Register bot commands
    register_bot_commands(bot)

    # Run the bot
    bot.run(credentials["bot_token"])
