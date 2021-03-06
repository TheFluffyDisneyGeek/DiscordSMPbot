import discord
# import dryscrape
import os
from discord.ext import commands
import traceback
import keep_alive
from dotenv import load_dotenv
load_dotenv(os.path.join('.env'))

bot = commands.Bot(command_prefix="/")


# https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5

initial_extensions = ['cogs.admincommands', 'cogs.minecraft', 'cogs.chat', 'cogs.listeners']

if __name__ == '__main__':
  for extension in initial_extensions:
      try:
        bot.load_extension(extension)
        print("loaded command {}".format(extension))
      except Exception as e:
        #print('Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()
  print("loaded commands!")


@bot.event
async def on_ready():
  print('Logged in as')
  print(bot.user.name)
  print(bot.user.id)
  print('copy paste this in your browser to authorize bot https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=268922066'.format(os.getenv('CLIENTID')))
  print('------')


keep_alive.keep_alive()    
bot.run(os.getenv('TOKEN'), bot=True, reconnect=True)
