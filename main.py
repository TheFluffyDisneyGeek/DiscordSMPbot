import discord
#import dryscrape
from discord.ext import commands
rebounding = 0
import sys, traceback


bot = commands.Bot(command_prefix="/")


#https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5

initial_extensions = ['admin','minecraft','chat','listeners']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
          bot.load_extension(extension)
        except Exception as e:
        
          print(f'Failed to load extension {extension}.', file=sys.stderr)
          traceback.print_exc()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('copy paste this in your browser to authorize bot https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=268922066'.format(os.environ['CLIENTID']))
    print('------')


    
bot.run(os.environ['TOKEN'], bot=True, reconnect=True)
