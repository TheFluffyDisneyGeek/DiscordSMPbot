import discord
from fuzzywuzzy import fuzz
from mcstatus import MinecraftServer
#import dryscrape
import asyncio
import os
from random import randint
from discord.ext import commands
rebounding = 0

class Shop:
  def __init__(self, name, inventory_pricing): 
    self.name = name
    self.inventory = inventory_pricing

#fluffShop = Shop("Fluffy's Shop",{"slimeballs":"1st|1d","bamboo":"2st|1d"})
endShop = Shop("End Shop",{"Elytra" : "1|25d","Shulker Boxes" : "1|1db"})
theShops = [endShop]

bot = commands.Bot(command_prefix="/")
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('copy paste this in your browser to authorize bot https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=268922066'.format(os.environ['CLIENTID']))
    print('------')



@bot.command()
async def ping(ctx):
  await ctx.send('Pong! {0} ms'.format(round(bot.latency *1000,2)))

@bot.command()
async def idklol(ctx):
  for channel in ctx.guild.channels:
    print(channel.name)

@bot.event
async def on_member_join(member):
  h_server = bot.get_guild(521322567911604244)
  joinGuild = member.guild
  if joinGuild == h_server:
    await member.send("")
    await member.send("Here is our website: https://justinwoolworth.wixsite.com/hermits ")
@bot.event
async def on_message(message):
  
  foof = bot.get_user(420741453690437652)
  mee = bot.get_user(159985870458322944)
  ninjacat = bot.get_user(405491673934856192)
  if message.author == ninjacat and randint(1,15) == 1:
    await message.add_reaction('<:businesscat:662732443668709406>')
  '''if message.author == mee:
    await message.channel.send("GO AWAY")'''

  if "link" in message.content and "claim" in message.content:
    await message.channel.send("link goes here")
  if "no u" in message.content and message.author != bot.user:
    await message.channel.send("no u")
  if randint(1,5) == 1:
    server = MinecraftServer.lookup("quacksmp.online")
    try:
      status = server.status()
      print("The server has {0} players, and replied in {1} ms.".format(status.players.online,status.latency))
    except:
      off = discord.Game("offline")
      await bot.change_presence(status = discord.Status.dnd ,activity = off)
    else:
      game = discord.Game("Now : {0}".format(status.players.online))
    if status.players.online == 0:
      await bot.change_presence(status = discord.Status.idle,activity = game)
    else:
      await bot.change_presence(activity = game)
  await bot.process_commands(message)


@bot.command(brief = "Check Prices.",description = "Usage: /shop itemname. Will throw error if incorrect spelling.")
async def shop(ctx,*,arg):
  ad = ["Want it delivered? Order it through Telestia Now!™","Our iron is blast mined so you dont have to farm it! Come to Ferrous Stone Hold for all your needs!","Come explore Ferrous Stone Hold and its many nooks and crannies!"]
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

@bot.command()
async def gicon(ctx):
  await ctx.send(ctx.guild.icon_url)

@bot.command(brief = "Remove cursed", description = "Needs message id")
async def cursed(ctx, arg):
  msg = await ctx.send("Message reported as cursed. Need 3 reactions to purge")
  await msg.add_reaction("✔")
  await ctx.message.delete()
  await ctx.trigger_typing()
  await asyncio.sleep(10)
  await ctx.trigger_typing()
  await asyncio.sleep(10)
  messid = msg.id
  mess = await ctx.fetch_message(messid)
  yeetus = mess.reactions[0]
  
  if yeetus.count >= 4:
    try:
      delmessid = int(arg)
    except:
      ctx.send("Error!")
      await msg.delete()
    else:
      delmess = await ctx.fetch_message(delmessid)
      await delmess.delete()
      await msg.delete()
      sucsess = await ctx.send("purged")
      await asyncio.sleep(7)
      await sucsess.delete()
  else:
    await ctx.send("not enough peeps")
    await msg.delete()
    
@bot.command()
@commands.has_any_role("Helper","Bot dev")
async def accept(ctx):
  welcome = ctx.message.mentions[0]
  embed = discord.Embed(name = "You were accepted!")
  embed.add_field(name = "You were accepted!",value = "Congratulations on being accepted! 🙂 Please read through the information channel before you join, and one of our admins will be on sometime soon to give you a tour and explain everything to you!")
  await welcome.send(embed = embed)
  role = discord.utils.get(ctx.guild.roles, name="Member")
  roledos = discord.utils.get(ctx.guild.roles, name = "Applicant")
  await welcome.add_roles(role)
  await welcome.remove_roles(roledos)
  await ctx.message.delete()
global errorMsg
errorMsg = ["Just. No.", "would you like a kumquat instead?","And why would I do a thing like that?","why have you awoken me from my slumber!? Who are you to call upon me? Hah, you are truly a fool!","You dare try to access my knowledge you foolish mortal? I shall smite you between my thumb and index finger if you do not apologize this instant!!!"] 

@bot.command(brief = "be happy", description = "No more sad :)")
async def sad(ctx):
  await ctx.message.delete()
  await ctx.channel.send("https://media1.tenor.com/images/04838d48fed5aa7cce9dd6501bf287db/tenor.gif?itemid=15565721")

@bot.command(brief = "QuackSMP Server Status", description = "See if the QuackSMP Server is up") #status
async def status(ctx):
  server = MinecraftServer.lookup("quacksmp.online")
  try:
    status = server.status()
    await ctx.send("The server has {0} players, and replied in {1} ms.".format(status.players.online,status.latency))
  except:
    off = discord.Game("offline")
    await ctx.send("Sorry, the server is offline :(")
    await bot.change_presence(status = discord.Status.dnd ,activity = off)
  else:
    game = discord.Game("Now : {0}".format(status.players.online))
    if status.players.online == 0:
      await bot.change_presence(status = discord.Status.idle,activity = game)
    else:
      await bot.change_presence(activity = game)
    print("e")


@bot.command(brief = "Suggest something", description = "No quotes anymore :)")
async def suggest(ctx,*,arg):
  suggestChan = bot.get_channel(709497001619751022)
  await ctx.message.delete()
  embed = discord.Embed(title = "New Suggestion!")
  embed.add_field(name = arg, value = "Vote using the emoji!")
  msg = await suggestChan.send(embed = embed)
  await msg.add_reaction("✔")
  await msg.add_reaction("❌")

@bot.command(brief = "Admin: deny suggestion", description = "/denysuggestion <id> <reason>")
@commands.has_any_role("Helper","Bot dev")
async def denysuggestion(ctx,arg1,*,args):

  await ctx.message.delete()
  delMessage = await ctx.fetch_message(int(arg1)) 
  oldSuggestion = delMessage.embeds[0].fields[0].name

  newEmbed = discord.Embed(color=0xEE1B1B)
  newEmbed.add_field(name = "Suggestion: " + oldSuggestion + " : denied!",value = "Reason: " + args)

  await delMessage.edit(embed = newEmbed)

@bot.command(brief = "Admin: accept suggestion", description = "/acceptsuggestion <messageid> <reason>")
@commands.has_any_role("Helper","Bot dev")
async def acceptsuggestion(ctx,arg1,*,args):

  await ctx.message.delete()

  delMessage = await ctx.fetch_message(int(arg1))
  oldSuggestion = delMessage.embeds[0].fields[0].name

  newEmbed = discord.Embed(color=0x17F862)
  newEmbed.add_field(name = "Suggestion: " + oldSuggestion + " : accepted!",value = "Reason: " + args)
  
  await delMessage.edit(embed = newEmbed)

@bot.command(brief = "vote on something", description = "No quotes anymore :)")
async def vote(ctx,*,arg):
  await ctx.message.delete()
  embed = discord.Embed(title = "-Voting!-")
  embed.add_field(name = arg, value = "Vote using the emoji!")
  msg = await ctx.send(embed = embed)
  await msg.add_reaction("🍎")
  await msg.add_reaction("🍐")
  await msg.add_reaction("🍊")
  await msg.add_reaction("🍋")
@bot.command(brief = "Telestia now order",description="Name: | Items: | Price: | Location: | Tip Amount: |") 
@commands.has_any_role("Member")
async def order(ctx,*,arg):
  await ctx.message.delete()
  msgchan = bot.get_channel(633114987212046336)
  await msgchan.send("New order: \n" + arg)
@bot.command(brief = "Admin: say something", description = "Say something") #say
@commands.has_any_role("Helper","Bot dev")
async def say(ctx,*,arg):
    await ctx.message.delete()
    await ctx.send(arg)


@bot.command(brief = "Admin: set bot status", description = "set status. will show Playing (status)") #say
@commands.has_any_role("Helper","Bot dev")
async def botstatus(ctx,*,arg):
  await ctx.message.delete()
  game = discord.Game(arg)
  await bot.change_presence(activity = game)
#add perms plz


@bot.command(category = "Admin" ,brief = " Admin: Start a countdown", description = "Enter amount of hours for countdown.")
@commands.has_any_role("Helper","Bot dev")
async def countdown(ctx,arg):
  print("maybe working")
  if rebounding == 1:
    print("Rebounding")
    await ctx.send("One in progress!")
  rebounding == 1
  print("yay")
  await ctx.message.delete()
  msg = await ctx.channel.send("Starting Countdown:")
  t = float(arg)
  t = t*60 #t is now num of minutes
  while t > 0:
    hours = int(t/60)
    minutes = int(t % 60)
    stringToSay = str("Remaining time:\n" + str(hours) + ":"+ str(minutes))
    await msg.edit(content = stringToSay)
    await asyncio.sleep(60)
    t -= 1
  await ctx.send("EVENT HAS STARTED")
  await msg.delete()
  rebound = 0
@countdown.error
async def countdown(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
      await ctx.send("Incorrect Permissions")
    


@bot.command(category = "Admin" , brief = "Admin Commands!", description = "Not much else to say lol.")  #help
@commands.has_any_role("Helper")
async def helpme(ctx):
  embed = discord.Embed(title="Help Menu", description="deprecated", color=0x00ff00)
  embed.add_field(name="Video for help", value="https://www.youtube.com/watch?v=dQw4w9WgXcQ", inline=False)
  await ctx.channel.send(embed=embed)
@helpme.error
async def helpme(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        randNum = randint(0,4)
        await ctx.channel.send(errorMsg[randNum])
@bot.command(category = "Admin" , brief = "Kick Newcomers", description = "Anyone with Newcomer role will be yeeted.")  #yeetmembers
@commands.has_any_role("Helper")
async def yeetmembers(ctx):
  print("working")
  await ctx.message.delete()
  role = discord.utils.get(ctx.message.guild.roles, name="Newcomer")
  if role is None:
      await ctx.channel.send('There is no "Newcomer" role on this server!')
      return
  for member in role.members:
    await member.send("You have been kicked. ")
    await ctx.channel.send(member.id)
    print("working so far")
    await ctx.guild.kick(ctx.guild.get_member(member.id))
    print("kicked")
@yeetmembers.error
async def yeetmembers(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
      randNum = randint(0,4)
      await ctx.channel.send(errorMsg[randNum])
@shop.error
async def shop(ctx,error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("You didn't say what you wanted! \n/shop all\n will show all shops.")
bot.run(os.environ['TOKEN'], bot=True, reconnect=True)
