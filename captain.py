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
# openai.api_key = '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'


@client.event
async def on_ready():
    print(f'The bot is ready for use!')
    print('--------------------------')

token = os.getenv('BARD_API_KEY')
discord_token = os.getenv('Discord_Token')
OPENAI_KEY = os.getenv('OPENAI_KEY')
BARD_API_KEY = os.getenv('BARD_API_KEY')

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

def generate_bard_image_description(file):
    try:
        prompt = "Explain this image"
        bard = Bard(token=BARD_API_KEY)
        response = requests.get(file)
        image_data = response.content

        bard_answer = bard.ask_about_image(prompt, image_data)
        print(bard_answer,"???????")

        if bard_answer:
            generated_text = bard_answer['content']
            return generated_text
        else:
            return "Image interpretation failed."
    except Exception as e:
        print(f'image genrate failed',str(e))

    
@client.event
async def on_message(message):
    global ticket_open
    print(message,"@@@@@")
    
    # if message.author.bot:
    # 

    if message.author.bot or "ticket" not in message.channel.name or isinstance(message.channel, discord.DMChannel):
        return
    content = message.content.lower()
    if content.startswith('/generate_image'):
        prompt = content[len('/generate_image'):].strip()
        
        if prompt:
            try:
                response = openai.Image.create(prompt=prompt, api_key=OPENAI_KEY)
                image_url = response['data'][0]['url']
                image_data = requests.get(image_url).content
                description = google_search(prompt)
                if description:
                    with open("image.png", "wb") as f:
                        f.write(image_data)
                    await message.channel.send(file=discord.File("image.png"))
                    await message.channel.send(f"Image Description: {description}")
                else:
                    await message.channel.send("Please provide a prompt for image description.")

            except Exception as e:
                await message.channel.send(f"Image generation failed: {str(e)}")
        else:
            await message.channel.send("Please provide a prompt for image generation.")
    elif content.startswith('/interpret_image'):
        if message.attachments:
            for attachment in message.attachments:
                generated_text = generate_bard_image_description(attachment)
                print('genreate text',generated_text)
                await message.channel.send(f"Image Description: {generated_text}")
        else:
            await message.channel.send("No image attachments found for interpretation.")
    else:
        content = message.content.lower()
        if content:
            print(content,"inside if")
            your_intro_prompt = f"""
            You are Girolamo, a large language model inspired by Italian Physicist Girolamo Cardano, is a versatile tool that can be used for many different purposes, including:

            Learning: Girolamo can help users learn new things by providing them with information from a variety of sources, including books, articles, and websites in english.
            Creation: Girolamo can help users create new content, such as poems, code, scripts, musical pieces, email, and letters.
            Entertainment: Girolamo can entertain users by telling stories, jokes, and playing games.
            Connection: Girolamo can help users connect with others by translating languages, writing letters, and generating creative content.
            Girolamo is still under development, but is learning and growing every day. Girolamo is committed to helping users in new and innovative ways.

            Prompt:

            User: {content}"""
            bard_response = google_search(your_intro_prompt)
            await message.channel.send(bard_response)
            await client.process_commands(message)
        else:
            await message.channel.send("No search results found.")
        if content.startswith('/open_ticket'):
            ticket_prompt = content[len('/open_ticket'):].strip()
            print(ticket_prompt,">>>>>")
            if ticket_prompt:
                if not ticket_open:
                    ticket_open = True
                    # Use Bard API or your appropriate API function to generate a response
                    bard_response = google_search(ticket_prompt)  # Use your function or API
                    print(bard_response,"+++++")
                    await message.channel.send(f"Ticket opened. Describe your issue\n{bard_response}.")
                else:
                    await message.channel.send("A ticket is already open. Close it to open a new one.")
            else:
                await message.channel.send("Please provide a prompt to open a ticket.")

        elif content.startswith('/close_ticket'):
            if ticket_open:
                ticket_open = False
                await message.channel.send("Ticket closed. Issue resolved.")
            else:
                await message.channel.send("No ticket is currently open.")

        await client.process_commands(message)


@client.event
async def on_error(event, *args, **kwargs):
    exception = kwargs.get('exception', None)
    if exception and isinstance(exception, discord.errors.ConnectionClosed):
        # Handle the ConnectionClosed error
        print(f"ConnectionClosed error: {exception}")

client.run(discord_token)
