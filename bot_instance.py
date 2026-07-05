import discord
from discord.ext import commands

# the one shared bot object every other file imports from
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)