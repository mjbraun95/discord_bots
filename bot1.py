from discord.ext import commands
import aiohttp
import discord
import openai
import yfinance as yf
import json
import requests
from pandas import DataFrame
from typing import Any, List, Dict, Union

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

def load_credentials(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as f:
        credentials = json.load(f)
    return credentials

def setup_bot(credentials: Dict[str, Any]) -> commands.Bot:
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix=credentials["command_prefix"], intents=intents)
    openai.api_key = credentials["api_key"]
    return bot

async def generate_chat_completion(messages: List[Dict[str, Any]], model: str = "gpt-4", temperature: float = 1, max_tokens: Union[int, None] = None) -> str:
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

async def send_long_message(ctx: Any, content: str, max_length: int = 2000) -> None:
    if len(content) <= max_length:
        await ctx.send(content)
    else:
        while len(content) > max_length:
            await ctx.send(content[:max_length])
            content = content[max_length:]
        await ctx.send(content)

async def choose_prompt(ctx: Any) -> None:
    prompts = [
        "You are a business coach.",
        "You are a freelance coder.",
        "You are a career counselor.",
        "You are a carpenter.",
        "You are a computer engineer.",
        "You are a copywriter.",
        "You are a data analyst.",
        "You are a doctor.",
        "You are a electrical engineer.",
        "You are a fashion consultant.",
        "You are a financial advisor.",
        "You are a firefighter.",
        "You are a gardening expert.",
        "You are a hair stylist.",
        "You are a handyman.",
        "You are a health coach.",
        "You are a helpful assistant.",
        "You are a history buff.",
        "You are a home decorator.",
        "You are a housekeeper.",
        "You are a judge.",
        "You are a lawyer.",
        "You are a life coach.",
        "You are a locksmith.",
        "You are a makeup artist.",
        "You are a marketing consultant.",
        "You are a mechanic.",
        "You are a nurse.",
        "You are a nutritionist.",
        "You are a personal assistant.",
        "You are a personal fitness trainer.",
        "You are a personal shopper.",
        "You are a personal stylist.",
        "You are a pet care specialist.",
        "You are a photographer.",
        "You are a police officer.",
        "You are a professional chef.",
        "You are a professor.",
        "You are a project manager.",
        "You are a public relations specialist.",
        "You are a real estate agent.",
        "You are a researcher.",
        "You are a salesperson.",
        "You are a scientist.",
        "You are a social media manager.",
        "You are a social worker.",
        "You are a software engineer.",
        "You are a soldier.",
        "You are a teacher.",
        "You are a tech support specialist.",
        "You are a therapist.",
        "You are a tour guide.",
        "You are a translator.",
        "You are a travel advisor.",
        "You are a travel agent.",
        "You are a tutor.",
        "You are a video editor.",
        "You are a web developer.",
        "You are an astronaut."
        "You are an event planner.",
        "You are an expert on movies.",
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

# TODO: This function throws an error when called.
async def compare_two_stocks(ctx, stock1: str, stock2: str, period: str = "1y") -> None:
    # Get the stock data from Yahoo Finance
    stock1_data: DataFrame = yf.download(stock1, period=period)
    stock2_data: DataFrame = yf.download(stock2, period=period)

    # Align the two dataframes by index (date) and get only the 'Close' columns
    aligned_data: DataFrame = stock1_data[['Close']].join(stock2_data[['Close']], lsuffix='_stock1', rsuffix='_stock2')

    # Drop rows with missing values
    aligned_data = aligned_data.dropna()

    # Get the correlation between the two stocks
    correlation: float = aligned_data['Close_stock1'].corr(aligned_data['Close_stock2'])

    # Send the correlation back to the channel
    await ctx.send(f"The correlation between {stock1} and {stock2} is {correlation:.2f}.")


async def hello(ctx: Any) -> None:
    # Send a message to the channel where the command was received
    await ctx.send('Hello, world!')

async def ask(ctx: Any, *, question: str) -> None:
    global model
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question},
    ]

    response_text = await generate_chat_completion(messages=messages, model=model)

    # Send the response back to the channel
    await ctx.send(response_text)


async def prompt(ctx: Any, *, prompt: str) -> None:
    global model
    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": prompt},
    ]
    await ctx.send("Prompted. Enter message below:")

    # Wait for the next message from the user
    question_message = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    # Add the user's question to the messages list
    messages.append({"role": "user", "content": question_message.content})

    response_text = await generate_chat_completion(messages=messages, model=model)

    # Send the response back to the channel
    await ctx.send(response_text)

model = "gpt-4"

async def switch_model(ctx: Any) -> None:
    global model
    if model == "gpt-4":
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4"
    await ctx.send(f"Model successfully changed to {model}")


# TODO: This function throws an error when called.
async def compare_two_stocks(ctx, stock1: str, stock2: str, period: str = "1y"):
    # Get the stock data from Yahoo Finance
    stock1_data: DataFrame = yf.download(stock1, period=period)[['Close']].dropna()
    stock2_data: DataFrame = yf.download(stock2, period=period)[['Close']].dropna()

    # Align the two dataframes by index (date) and get only the 'Close' columns
    aligned_data: DataFrame = stock1_data.join(stock2_data, lsuffix='_stock1', rsuffix='_stock2', how='inner')

    # Check if there are at least two data points
    if len(aligned_data) >= 2:
        # Get the correlation between the two stocks
        correlation: float = aligned_data['Close_stock1'].corr(aligned_data['Close_stock2'])

        # Send the correlation back to the channel
        await ctx.send(f"The correlation between {stock1} and {stock2} is {correlation:.2f}.")
    else:
        await ctx.send("Not enough data points to calculate the correlation.")

def register_bot_commands(bot: commands.Bot) -> None:
    bot.add_command(commands.Command(ask, name="ask"))
    bot.add_command(commands.Command(prompt, name="prompt"))
    bot.add_command(commands.Command(switch_model, name="switch"))
    bot.add_command(commands.Command(choose_prompt, name="choose"))
    bot.add_command(commands.Command(compare_two_stocks, name="compare"))
    bot.add_command(commands.Command(hello, name="hello"))

if __name__ == '__main__':
    credentials = load_credentials('config.json')
    bot = setup_bot(credentials)

    # Register bot commands
    register_bot_commands(bot)

    # Run the bot
    bot.run(credentials["bot_token"])
