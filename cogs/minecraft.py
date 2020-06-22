import discord
import pickle 
from discord.ext import commands
from fuzzywuzzy import fuzz
from random import randint
from mcstatus import MinecraftServer

class Shop:
  def __init__(self, name, inventory_pricing): 
    self.name = name
    self.inventory = inventory_pricing

pickledShops = {}
theShops = []


#fluffShop = Shop("Fluffy's Shop",{"test":"1st|1d"}) #example shop
#endShop = Shop("End Shop",{"Elytra" : "1|25d","Shulker Boxes" : "1|1db"})
#theShops = [endShop]



def dumpShops():
  file = open("storedVariables/vars.txt","r+")
  file.truncate(0)
  file.close()
  global pickledShops
  pickledShops = {}
  print(theShops)
  for s in theShops:
    pickledShops.update({s.name:s.inventory})
  with open("storedVariables/vars.txt", 'wb') as f:
    pickle.dump(pickledShops, f) 
  with open("storedVariables/backup.txt", 'wb') as f:
    pickle.dump(pickledShops, f)
  print("shops dumped!")


def loadShops():
  with open("storedVariables/vars.txt", 'rb') as f:
    try:
      stuffs = pickle.load(f)
    except:
      dumpShops()
      stuffs = pickle.load(f)
    for s in stuffs:
      print(s)
      theShops.append(Shop(s,stuffs.get(s)))
  print("Shops Loaded!")


loadShops()


class mCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  
  @commands.command()
  async def makeshop(self,ctx,*args):
    #await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
    user_inventory = {}
    try:
      int(args[1]);args[int(args[1])+2]
    except:
      await ctx.send("ERROR: Incorrect format, or you did not supply needed arguments")
      return
    for i in range(2,(int(args[1]) * 2) + 1):
      if i % 2 ==0:
        try:
          user_inventory.update({args[i]:args[i+1]})
        except:
          print("error," + str(i))
    theShops.append(Shop(args[0],user_inventory))
    dumpShops()
    await ctx.send("Shop created!")

    
  @commands.command(brief = "Check Prices.",description = "Usage: /shop itemname. Will throw error if incorrect spelling.")
  async def shop(self,ctx,*,arg):
    ad = ["insert ad here"]
    item = arg
    item = item.lower()
    found = []
    if arg == "all":
      for shopObject in theShops:
        for key in shopObject.inventory:
          found.append(shopObject.name + " : " + key + " : " + shopObject.inventory[key])
    else:
      for shopObject in theShops:
        for key in shopObject.inventory:
          if fuzz.partial_ratio(item.lower(),key.lower()) > 85:
            found.append(shopObject.name + " : " + key + " : " + shopObject.inventory[key])
    embed = discord.Embed(title = "Results:", color = 0x0099ff)
    found.sort()
    for i in found:
      embed.add_field(name = "------",value = i)
    if found == []:
      embed.add_field(name = "Error:", value = "could not find item. doesn't exist or incorrect spelling.")
    if randint(1,10) == 1:
      embed.add_field(name = "------",value = ad[randint(0,len(ad))])
    await ctx.send(embed = embed)

  @shop.error
  async def shop_error(self,ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send("You didn't say what you wanted! \n/shop all\n will show all shops.")

  @commands.command(brief = "QuackSMP Server Status", description = "See if the QuackSMP Server is up") #status
  async def status(self,ctx):
    server = MinecraftServer.lookup("quacksmp.online")
    try:
      status = server.status()
      await ctx.send("The server has {0} players, and replied in {1} ms.".format  (status.players.online,status.latency))
    except:
      off = discord.Game("offline")
      await ctx.send("Sorry, the server is offline :(")
      await self.bot.change_presence(status = discord.Status.dnd ,activity = off)
    else:
      game = discord.Game("Now : {0}".format(status.players.online))
      if status.players.online == 0:
        await self.bot.change_presence(status = discord.Status.idle,activity = game)
      else:
        await self.bot.change_presence(activity = game)


def setup(bot):
  bot.add_cog(mCommands(bot))
