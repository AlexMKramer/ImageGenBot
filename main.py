import os
from dotenv import load_dotenv
import discord

load_dotenv()

# Setup commands cog
bot = discord.Bot()
bot.auto_sync_commands = True
intents = discord.Intents.default()
bot.load_extension("core.generateCog")


@bot.event
async def on_guild_join(guild):
    print(f'Wow, I joined {guild.name}!')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='drawing tutorials.'))
    for guild in bot.guilds:
        print(f"I'm active in {guild.id} a.k.a {guild}!")


async def shutdown(bot_name):
    await bot_name.close()

if __name__ == '__main__':
    bot.run(os.getenv('BOT_TOKEN'))
