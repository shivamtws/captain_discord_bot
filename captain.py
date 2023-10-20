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

openai.api_key = "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"
def query(query):
    # Generate an image from a text description
    if query.startswith('/'):
        response = openai.Image.create(prompt=query)
        print('check redsponse',response.data)
        image_url = response['data'][0]['url']
        image_data = requests.get(image_url).content

        # Save the image to a file
        with open("image.png", "wb") as f:
            f.write(image_data)
        return image_data

client.run(discord_token)

# def google_search(query):
#     print('inside google search query',query)
#     data = query.split('>')
#     query_data = data[1]
    
#     # google_api_key = 'AIzaSyDSwL4umIZ4nYVsDJU76jzxzp_fvBHvGh4'
#     google_api_key = 'bgiLwrJaZFCwxdjV-TKpSQ6DymyoH5BlrWMQ4ypmtCX7oIV1xsAfEd5LlBare0OvGHzTFQ.'
#     # Replace 'YOUR_CX' with your actual Custom Search Engine ID (CX)
#     cx = '3512329d56c5e41d4'
#     base_url = 'https://www.googleapis.com/customsearch/v1'

#     url = f'{base_url}?key={google_api_key}&cx={cx}&q={query_data}'

#     response = requests.get(url)
#     print(response,"check response")
#     if response.status_code == 200:
#         data = response.json()
#         print('inside response',data)
#         items = data.get('items', [])

#         search_results = []
#         max_results = 3  
#         max_title_length = 100

#         for i, item in enumerate(items[:max_results], start=1):
#             title = item.get('title', f'Hotel {i}')
#             link = item.get('link', 'No link available')
#             snippet = item.get('snippet', 'No snippet available')

#             # Truncate titles if they exceed the maximum length
#             if len(title) > max_title_length:
#                 title = title[:max_title_length] + '...' 

#             # result_str = f'{i}. **{title}**\n{link}\n{snippet}\n'
#             result_str = f'{i}. {title}'
#             search_results.append(result_str)

#         # Combine the search results into a single string
#         formatted_results = '\n'.join(search_results)
#         return formatted_results
#     else:
#         return f'Error: {response.status_code}\n{response.text}'
    



