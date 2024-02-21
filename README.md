**Discord Finance and Chat Bot**

This codebase contains two main scripts for creating and running Discord bots with a focus on finance and chat functionalities. bot1.py is a more comprehensive bot that includes features such as stock comparisons, earnings updates, and dynamic chat completions using OpenAI's GPT models. bot2.py provides a simplified version focusing on chat interactions.

**Features**

Stock Comparisons and Earnings Updates: Utilizes Yahoo Finance and other financial data sources to provide users with up-to-date stock information and earnings dates.
Dynamic Chat Completions: Integrates OpenAI's GPT models to generate responses to user inquiries, offering a conversational AI experience within Discord.
Multiple Utility Commands: Includes commands for general interaction, such as greeting users and clearing conversation history.

**Setup**

Install Dependencies: Ensure you have Python 3.6+ installed. Then install the required packages using:
```bash
pip install -r requirements.txt
```

Configuration: Place your OpenAI API key, Discord bot token, and other necessary credentials in config.json.

Running the Bot: Use the following command to run your bot:

```bash
python bot1.py # For the comprehensive bot
# or
python bot2.py # For the simplified chat bot
```

**Usage**

After setting up your bot and inviting it to your Discord server, you can use the predefined commands to interact with it. For example, you can request stock comparisons, get upcoming earnings dates, or engage in a conversation with the chatbot powered by OpenAI.