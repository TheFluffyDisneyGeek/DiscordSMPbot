import discord
import datetime as dt
from discord.ext import commands
import asyncio
class chatCommands(commands.Cog,name = "Member commands"):
  def __init__(self, bot):
    self.bot = bot


  @commands.command(brief = "Remove cursed", description = "Needs message id")
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
    emotes = mess.reactions[0]  
    if emotes.count >= 4:
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


  @commands.command()
  async def ping(self,ctx):
    await ctx.send('Pong! {0} ms'.format(round(self.bot.latency *1000,2)))


  @commands.command(brief = "Suggest something", description = "No quotes anymore :)")
  async def suggest(self,ctx,*,arg):
    suggestChan = self.bot.get_channel(723526695902117909)
    await ctx.message.delete()
    embed = discord.Embed(title = "New Suggestion!")
    embed.add_field(name = arg, value = "Vote using the emoji!")
    msg = await suggestChan.send(embed = embed)
    await msg.add_reaction("✔")
    await msg.add_reaction("❌")

  @commands.command()
  async def gicon(ctx):
    await ctx.send(ctx.guild.icon_url)

  @commands.command(brief = "be happy", description = "No more sad :)")
  async def sad(self,ctx):
    await ctx.message.delete()
    await ctx.channel.send("https://media1.tenor.com/images/04838d48fed5aa7cce9dd6501bf287db/tenor.gif?itemid=15565721")

def setup(bot):
    bot.add_cog(chatCommands(bot))