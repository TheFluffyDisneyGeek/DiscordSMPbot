import discord
import datetime as dt
from discord.ext import commands
import cogs.admincommands as admin
import asyncio


class ChatCommands(commands.Cog, name="General commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Remove cursed", description="Needs message guildId")
    async def cursed(self, ctx, arg):
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
    async def ping(self, ctx):
        await ctx.send('Pong! {0} ms'.format(round(self.bot.latency * 1000, 2)))

    @commands.command(brief="Suggest something", description="No quotes anymore :)")
    async def suggest(self, ctx, *, arg):
        suggest_chan = self.bot.get_channel(723526695902117909)
        await ctx.message.delete()
        embed = discord.Embed(title="New Suggestion!")
        embed.add_field(name=arg, value="Vote using the emoji!")
        msg = await suggest_chan.send(embed=embed)
        await msg.add_reaction("✔")
        await msg.add_reaction("❌")

    @commands.command()
    async def gicon(self, ctx):
        await ctx.send(ctx.guild.icon_url)

    @commands.command()
    async def apply(self, ctx: discord.ext.commands.Context):
        server = admin.get_server(ctx.message.guild.id)
        if not len(server.applicationFormat) > 0:
            await ctx.send("Uh oh. Applications have not been set up")
            return
        else:
            applicant = ctx.message.author
            await ctx.send("Please check your dm!")
            full_application = []

            def check(message):
                return message.author.id == applicant.id and isinstance(message.channel, discord.channel.DMChannel)

            embed = discord.Embed()
            embed.add_field(name="Application",
                            value="To fill out your application, just answer the questions that are sent to you. You "
                                  "will have 5 minutes to answer each question. You have 5 minutes to reply \"START\" "
                                  "to begin.", inline=False)
            await ctx.send(embed=embed)
            try:
                context = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return
            await applicant.send("Starting!")
            for msg in server.applicationFormat:
                msg2 = str(msg)
                msg2.split(":")
                question = msg2[0]
                context = msg2
                conditions = msg2[2:]
                embed = discord.Embed()
                embed.add_field(name=question,
                                value=context, inline=False)
                await ctx.send(embed=embed)
                try:
                    response = await self.bot.wait_for("message", timeout=300.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send("Timeout: please restart this process.")
                    return
                full_application.append(question + ":" + response)
            applicant.send("Thank you for filling out the form! Please await a response.")
            embed = discord.Embed(title=applicant.name + "'s Application")
            for i in full_application:
                i2 = i.split(":")
                embed.add_field(name=i2[0], value=i2[1])
            await self.bot.get_channel(server.appChannel).send(embed=embed)


    @commands.command(brief="be happy", description="No more sad :)")
    async def sad(self, ctx):
        await ctx.message.delete()
        await ctx.channel.send(
            "https://media1.tenor.com/images/04838d48fed5aa7cce9dd6501bf287db/tenor.gif?itemid=15565721")


def setup(bot):
    bot.add_cog(ChatCommands(bot))
