import asyncio
import discord
from discord.ext import commands
import requests
from bardapi import Bard
import bardapi
import os
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from retrying import retry

load_dotenv()


# Create a Discord bot instance with the correct command_prefix
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix ='!', intents=intents)


@client.event
async def on_ready():
    print(f'The bot is ready for use!')
    print('--------------------------')

token = os.getenv('BARD_API_KEY')
if not token:
    raise ValueError("BARD_API_KEY environment variable not set")

bard = Bard(token=token)

@retry(
    retry_on_exception=lambda exc: isinstance(exc, ReadTimeout),
    wait_exponential_multiplier=1000,  # Wait for 1 second, then 2 seconds, 4 seconds, etc.
    stop_max_attempt_number=3,  # Maximum of 3 retries
)
def perform_search(query):
    try:
        response = bard.get_answer(query)
        if response:
            return response['content']
        else:
            return "No search results found."
    except ReadTimeout:
        raise ReadTimeout("Bard API request timed out")
    
def google_search(query):
    try:
        content = perform_search(query)
        print(content)
        return content
    except ReadTimeout:
        return "Bard API request timed out. Please try again."

    
@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    print(message.content.startswith('!google'))
    if message.content:
        query = message.content[len('!google'):].strip()
        search_results =  google_search(query)
        if search_results:
            await message.reply(search_results)
        else:
            # Handle the case where no search results are found
            await message.reply("No search results found.")

    await client.process_commands(message)

key = os.getenv("key")

client.run(key)


