import discord
from discord.ext import commands
from random import randint
import cogs.admincommands as admin


class BotListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        message = admin.get_server(member.guild.id).important_messages.get("welcome")
        if message is not None:
            await member.send(message)


    # @commands.Cog.listener()
    # async def on_message(self, message):
    #    if "no u " in message.content and message.author != self.bot.user:
    #        await message.channel.send("no u")
    #    await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(BotListeners(bot))
