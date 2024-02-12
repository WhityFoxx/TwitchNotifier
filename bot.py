import discord
from config import TOKEN
bot = discord.Bot(intents=discord.Intents.all())
bot.load_extension('cogs.twitchcog')
bot.run(TOKEN)