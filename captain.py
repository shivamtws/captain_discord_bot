import asyncio
import discord
from discord.ext import commands
import requests
from bardapi import Bard
import bardapi
import os
from requests.exceptions import ReadTimeout
from retrying import retry
import openai
from dotenv import load_dotenv

load_dotenv()


# Create a Discord bot instance with the correct command_prefix
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix ='!', intents=intents)
ctx = '3512329d56c5e41d4'
google_api_key = 'AIzaSyDSwL4umIZ4nYVsDJU76jzxzp_fvBHvGh4'
# query = 'top five hotel in chandigarh'

@client.event
async def on_ready():
    print(f'The bot is ready for use!')
    print('--------------------------')

token = os.getenv('BARD_API_KEY')
discord_token = os.getenv('Discord_Token')

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
        print('query',query)
        content = perform_search(query)
        print(content)
        return content
    except ReadTimeout:
        return "Bard API request timed out. Please try again."

@client.event
async def on_message(message):
    if (message.author.bot == True):
        return 
    if  message.content.lower():
        query = message.content
        search_results = google_search(query)
        if search_results:
            await message.channel.send(search_results)
        else:
            await message.channel.send("No search results found.")

    await client.process_commands(message)

client.run(discord_token)  



