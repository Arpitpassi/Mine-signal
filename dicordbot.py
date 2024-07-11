import discord
import requests
import os

TOKEN = os.environ.get("TOKEN")
ESP8266_IP = '192.168.177.49'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(TOKEN)
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if 'minecraft' in message.content.lower():
        print("Something in the way")  # This line prints to the console
        await message.channel.send("Something in the way")  # This line sends the message to the Discord channel
        response = requests.get(f'http://{ESP8266_IP}/toggle')
        if response.status_code == 200:
            await message.channel.send('Light toggled!')
        else:
            await message.channel.send('Failed to toggle light.')

client.run(TOKEN)