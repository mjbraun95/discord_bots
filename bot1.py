from discord.ext import commands
from pandas import DataFrame
from typing import Any, List, Dict, Union
import aiohttp
import discord
import json
import numpy as np
import openai
import requests
import yfinance as yf
from tabulate import tabulate

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


async def compare_two_stocks(ctx, stock1: str, stock2: str, period: str = "1y"):
    # Get the stock data from Yahoo Finance
    stock1_data: DataFrame = yf.download(stock1, period=period)[['Close']].dropna()
    stock2_data: DataFrame = yf.download(stock2, period=period)[['Close']].dropna()

    # Align the two dataframes by index (date) and get only the 'Close' columns
    aligned_data: DataFrame = stock1_data.join(stock2_data, lsuffix='_stock1', rsuffix='_stock2', how='inner')

    # Check if there are at least two data points
    if len(aligned_data) >= 2:
        # Calculate basic statistics for each stock
        stock1_mean = aligned_data['Close_stock1'].mean()
        stock2_mean = aligned_data['Close_stock2'].mean()

        stock1_median = aligned_data['Close_stock1'].median()
        stock2_median = aligned_data['Close_stock2'].median()

        stock1_std = aligned_data['Close_stock1'].std()
        stock2_std = aligned_data['Close_stock2'].std()

        # Calculate the percentage change for each stock
        stock1_pct_change = aligned_data['Close_stock1'].pct_change().dropna()
        stock2_pct_change = aligned_data['Close_stock2'].pct_change().dropna()

        # Calculate the covariance and correlation between the two stocks
        covariance = np.cov(stock1_pct_change, stock2_pct_change)[0][1]
        correlation = np.corrcoef(stock1_pct_change, stock2_pct_change)[0][1]

        # Get market data for beta calculation
        market_data: DataFrame = yf.download('^GSPC', period=period)[['Close']].dropna()
        aligned_market_data: DataFrame = stock1_data.join(market_data, rsuffix='_market', how='inner')
        market_pct_change = aligned_market_data['Close_market'].pct_change().dropna()

        # Calculate beta for each stock
        stock1_beta = np.cov(stock1_pct_change, market_pct_change)[0][1] / np.var(market_pct_change)
        stock2_beta = np.cov(stock2_pct_change, market_pct_change)[0][1] / np.var(market_pct_change)

        # Calculate cumulative returns for each stock
        stock1_cumulative_return = (1 + stock1_pct_change).cumprod()[-1] - 1
        stock2_cumulative_return = (1 + stock2_pct_change).cumprod()[-1] - 1

        # Send the statistics back to the channel
        # Send the statistics back to the channel
        table_data = [
            ["Mean", f"{stock1_mean:.2f}", f"{stock2_mean:.2f}"],
            ["Median", f"{stock1_median:.2f}", f"{stock2_median:.2f}"],
            ["Standard Deviation", f"{stock1_std:.2f}", f"{stock2_std:.2f}"],
            ["Covariance", f"{covariance:.8f}", ""],
            ["Correlation Coefficient", f"{correlation:.2f}", ""],
            ["Beta", f"{stock1_beta:.2f}", f"{stock2_beta:.2f}"],
            ["Cumulative Returns", f"{stock1_cumulative_return:.2%}", f"{stock2_cumulative_return:.2%}"]
        ]

        response = f"**Statistics for {stock1} and {stock2}**\n"
        response += f"```{tabulate(table_data, headers=[stock1, stock2], tablefmt='grid')}```"
        # response = f"**Statistics for {stock1} and {stock2}**\n"
        # response += f"Mean: {stock1_mean:.2f}, {stock2_mean:.2f}\n"
        # response += f"Median: {stock1_median:.2f}, {stock2_median:.2f}\n"
        # response += f"Standard Deviation: {stock1_std:.2f}, {stock2_std:.2f}\n"
        # response += f"Covariance: {covariance:.8f}\n"
        # response += f"Correlation Coefficient: {correlation:.2f}\n"
        # response += f"Beta: {stock1_beta:.2f}, {stock2_beta:.2f}\n"
        # response += f"Cumulative Returns: {stock1_cumulative_return:.2%}, {stock2_cumulative_return:.2%}"
        await ctx.send(response)
    else:
        await ctx.send("Not enough data points to calculate the statistics.")
    global model
    # Call OpenAI's API to generate a response
    print("Compare the stock prices and provide insights of {stock1} and {stock2} of the past {period}. Here is some information about {stock1} and {stock2}:\n{table_data}".format(stock1=stock1, stock2=stock2, period=period, table_data=table_data))
    messages = [
        {"role": "system", "content": "You are a highly skilled wall street stock market expert."},
        {"role": "user", "content": "Compare the stock prices and provide insights of {stock1} and {stock2} of the past {period}. Here is some information about {stock1} and {stock2}:\n{table_data}".format(stock1=stock1, stock2=stock2, period=period, table_data=table_data)}
    ]

    response_text = await generate_chat_completion(messages=messages, model=model)
    await send_long_message(ctx, response_text)

# async def compare_two_stocks(ctx, stock1: str, stock2: str, period: str = "1y") -> None:
#     # Get the stock data from Yahoo Finance
#     stock1_data: DataFrame = yf.download(stock1, period=period)
#     stock2_data: DataFrame = yf.download(stock2, period=period)

#     # Get market data for beta calculation
#     market_data: DataFrame = yf.download('^GSPC', period=period)

#     # Align the dataframes by index (date) and get only the 'Close' columns
#     aligned_data: DataFrame = stock1_data[['Close']].join(stock2_data[['Close']], lsuffix='_stock1', rsuffix='_stock2').join(market_data[['Close']], rsuffix='_market')

#     # Drop rows with missing values
#     aligned_data = aligned_data.dropna()

#     # Calculate basic statistics for each stock
#     stock1_mean = aligned_data['Close_stock1'].mean()
#     stock2_mean = aligned_data['Close_stock2'].mean()

#     stock1_median = aligned_data['Close_stock1'].median()
#     stock2_median = aligned_data['Close_stock2'].median()

#     stock1_std = aligned_data['Close_stock1'].std()
#     stock2_std = aligned_data['Close_stock2'].std()

#     # Calculate the percentage change for each stock and the market
#     stock1_pct_change = aligned_data['Close_stock1'].pct_change().dropna()
#     stock2_pct_change = aligned_data['Close_stock2'].pct_change().dropna()
#     market_pct_change = aligned_data['Close_market'].pct_change().dropna()

#     # Calculate the covariance and correlation between the two stocks
#     covariance = np.cov(stock1_pct_change, stock2_pct_change)[0][1]
#     correlation = np.corrcoef(stock1_pct_change, stock2_pct_change)[0][1]

#     # Calculate beta for each stock
#     stock1_beta = np.cov(stock1_pct_change, market_pct_change)[0][1] / np.var(market_pct_change)
#     stock2_beta = np.cov(stock2_pct_change, market_pct_change)[0][1]

#     # Calculate cumulative returns for each stock
#     stock1_cumulative_return = (1 + stock1_pct_change).cumprod()[-1] - 1
#     stock2_cumulative_return = (1 + stock2_pct_change).cumprod()[-1] - 1

#     # Send the statistics back to the channel
#     response = f"**Statistics for {stock1} and {stock2}**\n"
#     response += f"Mean: {stock1_mean:.2f}, {stock2_mean:.2f}\n"
#     response += f"Median: {stock1_median:.2f}, {stock2_median:.2f}\n"
#     response += f"Standard Deviation: {stock1_std:.2f}, {stock2_std:.2f}\n"
#     response += f"Covariance: {covariance:.8f}\n"
#     response += f"Correlation Coefficient: {correlation:.2f}\n"
#     response += f"Beta: {stock1_beta:.2f}, {stock2_beta:.2f}\n"
#     response += f"Cumulative Returns: {stock1_cumulative_return:.2%}, {stock2_cumulative_return:.2%}"

#     await ctx.send(response)



async def hello(ctx: Any) -> None:
    # Send a message to the channel where the command was received
    await ctx.send('Hello, world!')

conversation_history = []

# TODO: test
async def ask(ctx: Any, *, question: str) -> None:
    global model
    global conversation_history

    # Add the new question to the conversation history
    conversation_history.append({"role": "user", "content": question})

    # Call OpenAI's API to generate a response
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *conversation_history
    ]

    response_text = await generate_chat_completion(messages=messages, model=model)

    # Add the assistant's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response_text})

    # Send the response back to the channel
    await ctx.send(response_text)

# async def ask(ctx: Any, *, question: str) -> None:
#     global model
#     # Call OpenAI's API to generate a response
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": question},
#     ]

#     response_text = await generate_chat_completion(messages=messages, model=model)

#     # Send the response back to the channel
#     await ctx.send(response_text)


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
