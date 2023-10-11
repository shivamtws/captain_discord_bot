import asyncio
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Create a Discord bot instance with the correct command_prefix
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix ='!', intents=intents)
ctx = '3512329d56c5e41d4'
google_api_key = 'AIzaSyDSwL4umIZ4nYVsDJU76jzxzp_fvBHvGh4'
query = 'top five hotel in chandigarh'

@client.event
async def on_ready():
    print(f'The bot is ready for use!')
    print('--------------------------')


# @client.event
# async def on_message(message):
    
#     print("+++++++++",message)
#     if message.author == client.user:
#         return
#     content = message.content
    
#     # Now you can process the content as needed
#     print(f"Received message: {content}")
#     # Check if the message content contains "hello"
#     if message.content.lower():
#         search_results = google_search(query)
#         await message.reply('hello, i am trickyyyy')

#     await client.process_commands(message)
def google_search(query):
    print('inside google search query',query)
    data = query.split('>')
    query_data = data[1]
    
    google_api_key = 'AIzaSyDSwL4umIZ4nYVsDJU76jzxzp_fvBHvGh4'
    # Replace 'YOUR_CX' with your actual Custom Search Engine ID (CX)
    cx = '3512329d56c5e41d4'
    base_url = 'https://www.googleapis.com/customsearch/v1'

    url = f'{base_url}?key={google_api_key}&cx={cx}&q={query_data}'
    print(url,"@@@@@@@@#########")

    response = requests.get(url)
    print(response,"check response")
    if response.status_code == 200:
        data = response.json()
        print('inside response',data)
        items = data.get('items', [])

        search_results = []
        max_results = 3  
        max_title_length = 50

        for i, item in enumerate(items[:max_results], start=1):
            title = item.get('title', f'Hotel {i}')
            link = item.get('link', 'No link available')
            snippet = item.get('snippet', 'No snippet available')

            # Truncate titles if they exceed the maximum length
            if len(title) > max_title_length:
                title = title[:max_title_length] + '...' 

            # result_str = f'{i}. **{title}**\n{link}\n{snippet}\n'
            result_str = f'{i}. {title}'
            search_results.append(result_str)

        # Combine the search results into a single string
        formatted_results = '\n'.join(search_results)
        return formatted_results
    else:
        return f'Error: {response.status_code}\n{response.text}'
    
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


