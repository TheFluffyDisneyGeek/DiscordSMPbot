import discord
from discord.ext import commands
from random import randint
from mcstatus import MinecraftServer
from admin import serverList

class botListeners(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_member_join(self,member):
    h_server = self.bot.get_guild(521322567911604244)
    joinGuild = member.guild
    if joinGuild == h_server:
      await member.send("")
      await member.send("Here is our website: https://justinwoolworth.wixsite.com/hermits ")

  @commands.Cog.listener()
  async def on_message(self,message):
    if "no u" in message.content and message.author != self.bot.user:
      await message.channel.send("no u")
    if randint(1,5) == 1:
      server = MinecraftServer.lookup("play.quacksmp.com")
      status = server.status()
      try:
        status = server.status()
        print("The server has {0} players, and replied in {1} ms.".format(status.players.online,status.latency))
      except:
        off = discord.Game("offline")
        await self.bot.change_presence(status = discord.Status.dnd ,activity = off)
      else:
        game = discord.Game("Now : {0}".format(status.players.online))
      if status.players.online == 0:
        await self.bot.change_presence(status = discord.Status.idle,activity = game)
      else:
        await self.bot.change_presence(activity = game)


def setup(bot):
   bot.add_cog(botListeners(bot))