import os
from io import BytesIO
import discord
import openai
import requests
from bardapi import Bard
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
from requests.exceptions import ReadTimeout
from retrying import retry

load_dotenv()

discord_token = os.getenv('Discord_Token')
OPENAI_KEY = os.getenv('OPENAI_KEY')
BARD_API_KEY = os.getenv('BARD_API_KEY')

if not BARD_API_KEY:
    raise ValueError("BARD_API_KEY environment variable not set")

bard = Bard(token=BARD_API_KEY)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'The bot is ready for use!')
    print('--------------------------')


@retry(
    retry_on_exception=lambda exc: isinstance(exc, ReadTimeout),
    wait_exponential_multiplier=1000,  # Wait for 1 second, then 2 seconds, 4 seconds, etc.
    stop_max_attempt_number=3,  # Maximum of 3 retries
)
# get description from image generate
def generate_bard_image_description(file):
    try:
        prompt = "Explain this image"
        response = requests.get(file)
        image_data = response.content
        bard_answer = bard.ask_about_image(prompt, image_data)
        if bard_answer:
            generated_text = bard_answer['content']
            return generated_text
        else:
            return "Please wait a few minutes, while I try to process your request OR try again after a few minutes.."
    except Exception as e:
        print(e)


def google_search_data(query):
    # Set the environment variable consistently
    session = requests.Session()
    session.headers = {
        "Host": "bard.google.com",
        "X-Same-Domain": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.114 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://bard.google.com",
        "Referer": "https://bard.google.com/",
        "Cookie": f"__Secure-1PSID={BARD_API_KEY}"  # Pass the API key via Cookie header
    }

    bard_answer = Bard(token=BARD_API_KEY, session=session, timeout=30)
    prompt = query
    # Continue the conversation
    response = bard_answer.get_answer(prompt)

    return response['content']


clients = OpenAI(api_key=OPENAI_KEY)
openai.api_key = OPENAI_KEY


def interpret_image(image_url):
    client = openai.OpenAI(api_key=OPENAI_KEY)
    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What’s in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{image_url}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        # print("response", response, "\n")

        # Accessing content based on the provided JSON structure
        content = response.choices[0].message.content

        # print(content)
        return content
    except Exception as e:
        print(e)


@bot.event
async def on_message(message):
    # print("encountered user:\n", message, "\n")
    if message.author.bot or isinstance(message.channel, discord.DMChannel):
        return
    if message.channel.name != "girolamo-chat":
        return
    await message.channel.typing()

    content = message.content.lower()
    # print("User Message:", content, "\n")

    if content.startswith('/generate_image'):
        prompt = content[len('/generate_image'):].strip()
        response = clients.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        # print("response", response, "\n")
        image_url = response.data[0].url

        image_get = requests.get(image_url)
        image_data = image_get.content
        image_io = BytesIO(image_data)

        await message.channel.typing()
        with open("image.png", "wb") as f:
            f.write(image_data)
        await message.channel.send(file=discord.File(image_io, "image.png"))
        await message.channel.typing()
        response = clients.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Explain this image ?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        await message.channel.typing()
        await message.channel.send(response.choices[0].message.content)

    elif content.startswith('/interpret_image'):
        if message.attachments:
            await message.channel.typing()
            # print('image url:', message.attachments, "\n")
            for attachment in message.attachments:
                await message.channel.typing()
                # print('check attachment', attachment)
                generated_text = interpret_image(attachment)
                await message.channel.typing()
                # print('generate text', generated_text)
                await message.channel.send(f"Image Description: {generated_text}")
        else:
            await message.channel.send("No image attachments found for interpretation.")
    elif content.startswith('/interpret_image'):
        if message.attachments:
            await message.channel.typing()
            # print('image url:', message.attachments, "\n")
            for attachment in message.attachments:
                await message.channel.typing()
                # print('check attachment', attachment)
                generated_text = interpret_image(attachment)
                await message.channel.typing()
                # print('generate text', generated_text)
                await message.channel.send(f"Image Description: {generated_text}")
        else:
            await message.channel.send("No image attachments found for interpretation.")
    else:
        content = message.content.lower()
        if content:
            await message.channel.typing()
            your_intro_prompt = f""" You are Girolamo, a large language model inspired by Italian Physicist Girolamo 
            Cardano, is a versatile tool that can be used for many different purposes, including:

            Learning: Girolamo can help users learn new things by providing them with information from a variety of 
            sources, including books, articles, and websites in english. Creation: Girolamo can help users create new 
            content, such as poems, code, scripts, musical pieces, email, and letters. Entertainment: Girolamo can 
            entertain users by telling stories, jokes, and playing games. Connection: Girolamo can help users connect 
            with others by translating languages, writing letters, and generating creative content. Girolamo is still 
            under development, but is learning and growing every day. Girolamo is committed to helping users in new 
            and innovative ways. And Please Response in English language if there is no Specific language is required.

            Prompt: {content}
            """

            async with message.channel.typing():
                bard_response = google_search_data(your_intro_prompt)

                handle_error_messages = ["Response Error", "Unable to get response"]
                if any(error_message in bard_response for error_message in handle_error_messages):
                    bard_response = ("Please wait a few minutes while I am processing your request OR try again after "
                                     "a few minutes later!!!")
                    return await message.channel.send(bard_response)
                await message.channel.typing()
                # Check if the response is too long
                if len(bard_response) > 2000:
                    # Split the response into parts
                    parts = [bard_response[i:i + 2000] for i in range(0, len(bard_response), 2000)]

                    # Send each part in a separate message
                    for part in parts:
                        await message.channel.typing()
                        await message.channel.send(part)
                else:
                    await message.channel.typing()
                    await message.channel.send(bard_response)

            await bot.process_commands(message)
        else:
            await message.channel.send("No search results found.")


bot.run(discord_token)
