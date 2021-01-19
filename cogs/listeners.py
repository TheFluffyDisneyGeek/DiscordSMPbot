import discord
from discord.ext import commands
from random import randint
from mcstatus import MinecraftServer
import cogs.admincommands as admin


class BotListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
      await member.send(admin.get_server(member.guild.id).importantMessages.get("welcome"))

    #@commands.Cog.listener()
    #async def on_message(self, message):
    #    if "no u " in message.content and message.author != self.bot.user:
    #        await message.channel.send("no u")
    #    await self.bot.process_commands(message)
    


def setup(bot):
    bot.add_cog(BotListeners(bot))
