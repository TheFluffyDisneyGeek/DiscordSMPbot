import discord
from discord.ext import commands
import asyncio
rebounding = 0

class adminCommands(commands.Cog,name = "Admin Commands"):
  def __init__(self, bot):
    self.bot = bot


  @commands.command(brief = "Admin: say something", description = "Say something") #say
  @commands.has_any_role("Helper","Bot dev")
  async def say(ctx,*,arg):
    await ctx.message.delete()
  
    await ctx.send(arg)

  @commands.command(brief = "Admin: set bot status", description = "set status. will show Playing (status)")
  @commands.has_any_role("Gamer","Bot dev")
  async def botstatus(self,ctx,*,arg):
    await ctx.message.delete()
    game = discord.Game(arg)
    await self.bot.change_presence(activity = game)


  @commands.command(category = "Admin" , brief = "Kick Newcomers", description = "Anyone with Newcomer role will be yeeted.")
  @commands.has_any_role("Helper")
  async def yeetmembers(self,ctx):
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
      await ctx.send("n o")


  @commands.command(category = "Admin" ,brief = " Admin: Start a countdown", description = "Enter amount of hours for countdown.")
  @commands.has_any_role("Helper","Bot dev")
  async def countdown(ctx,arg):
    print("maybe working")
    global rebounding
    if rebounding == 1:
      print("Rebounding")
      await ctx.send("One in progress!")
    rebounding = 1
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
    rebounding = 0

  @countdown.error
  async def countdown(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
      await ctx.send("Incorrect Permissions")


  @commands.command()
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


  @commands.command(brief = "Admin: accept suggestion", description = "/acceptsuggestion <messageid> <reason>")
  @commands.has_any_role("Helper","Bot dev")
  async def acceptsuggestion(ctx,arg1,*,args):
    await ctx.message.delete()
    delMessage = await ctx.fetch_message(int(arg1))
    oldSuggestion = delMessage.embeds[0].fields[0].name
    newEmbed = discord.Embed(color=0x17F862)
    newEmbed.add_field(name = "Suggestion: " + oldSuggestion + " : accepted!",value = "Reason: " + args)  
    await delMessage.edit(embed = newEmbed)


  @commands.command(brief = "Admin: deny suggestion", description = "/denysuggestion <id> <reason>")
  @commands.has_any_role("Helper","Bot dev")
  async def denysuggestion(ctx,arg1,*,args):
    await ctx.message.delete()
    delMessage = await ctx.fetch_message(int(arg1)) 
    oldSuggestion = delMessage.embeds[0].fields[0].name
    newEmbed = discord.Embed(color=0xEE1B1B)
    newEmbed.add_field(name = "Suggestion: " + oldSuggestion + " : denied!",value = "Reason: " + args)
    await delMessage.edit(embed = newEmbed)


#https://gist.github.com/OneEyedKnight/f0411f9a5e9dea23b96be0bf6dd86d2d
def setup(bot):
    bot.add_cog(adminCommands(bot))