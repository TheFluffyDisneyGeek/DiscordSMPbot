import json
from json.decoder import JSONDecodeError
import discord
from discord.ext import commands
import asyncio
import traceback
import cogs.minecraft
rebounding = 0


class Server:
    def __init__(self, serverid):
        self.id = serverid
        self.shopList = []
        self.appChannel = None
        self.suggestChannel = None
        self.serverAddress = None
        self.importantMessages = {}
        self.applicationFormat = []  # format: "question:required/not:image?:points"


def load_everything() -> list:
    with open("storedVariables/vars.txt", 'r', encoding='utf-8') as f:
        try:
            jsonlist = json.load(f)  # python list of json values
        except JSONDecodeError:
            print("Error! Initializing empty list!")
            return []
        print("Successfully loaded data")
        python_server_list = []  # python list of python dict values
        for jsonserver in jsonlist:
            python_server_list.append(json.loads(jsonserver))
        class_server_list = []  # python list of Server class values to return for the ServerList
        for server_dict in python_server_list:
            python_shop_list = []  # python list of python dict values for the shops
            jsonshoplist = server_dict.get('shopList')  # python list, full of json
            for jsonshop in jsonshoplist:
                python_shop_list.append(json.loads(jsonshop))
            class_shop_list = []  # python list of Shop class values for putting into the shop's attribute
            for dict_shop in python_shop_list:
                class_shop_list.append(cogs.minecraft.Shop(dict_shop.get('name'), dict_shop.get('inventory'), dict_shop.get('ownerid')))
            init_server = Server(server_dict.get('id'))  # make a server for us to initialize all the stored values.
            init_server.shopList = class_shop_list
            init_server.appChannel = server_dict.get('appChannel')
            init_server.suggestChannel = server_dict.get('suggestChannel')
            init_server.serverAddress = server_dict.get('serverAddress')
            init_server.importantMessages = server_dict.get('importantMessages')
            init_server.applicationFormat = server_dict.get('applicationFormat')
            class_server_list.append(init_server)
            print("Server {0} Processed. \n AppChannel:{1} \n suggestChannel:{2} \n serverAddress:{3} \n ImportantMessages: {4} \napplicationFormat: {5}".format(init_server.id, init_server.appChannel, init_server.suggestChannel, init_server.serverAddress, init_server.importantMessages, init_server.applicationFormat))
        return class_server_list


def save_everything():
    with open("storedVariables/vars.txt", 'w', encoding='utf-8') as f:
        alt_server_list = []
        for serv in serverList:
            alt_shop_list = []
            print(serv.shopList)
            if len(serv.shopList) > 0:
                for shop in serv.shopList:
                    alt_shop_list.append(json.dumps(shop.__dict__))
            serv.shopList = alt_shop_list
            alt_server_list.append(json.dumps(serv.__dict__))
        with open("storedVariables/vars.txt", "r", encoding="utf-8") as f2:
            backup = f2.read()
        try:    
            json.dump(alt_server_list, f)
        except TypeError:
            print("TypeError. Again.")
            f.write(backup)
            traceback.print_exc()
        f2.close()
        f.close()


def get_server(guild_id: int) -> Server:  # get the server, if not found make a new one, save and return new one
    for serv in serverList:
        if serv.id == guild_id:
            return serv
    new_server = Server(guild_id)
    serverList.append(new_server)
    return new_server


serverList = load_everything()


class AdminCommands(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command(brief="Admin: say something", description="Say something")  # say
    @commands.has_any_role("admin")
    async def say(self, ctx, *, arg):
        await ctx.message.delete()
        await ctx.send(arg)

    @commands.command(brief="Dev Only: set bot status", description="set status. will show Playing (status)")
    @commands.is_owner()
    async def botstatus(self, ctx, *, arg):
        await ctx.message.delete()
        game = discord.Game(arg)
        await self.bot.change_presence(activity=game)

    @commands.group(brief="Setup server with different subcommands",
                    description="usage: /setup (command options ->) "
                                "<ip:application:appchannel:suggestchannel:messages:>")
    @commands.has_any_role("admin")
    async def setup(self, ctx: discord.ext.commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid setup command passed')

    @setup.command()
    @commands.has_any_role("admin")
    async def ip(self, ctx, *, args):
        serv = get_server(ctx.guild.id)
        serv.serverAddress = args
        await ctx.send("Server ip setup as:" + args)
        save_everything()

    @setup.command()
    @commands.has_any_role("admin")
    async def application(self, ctx: discord.ext.commands.Context):
        serv = get_server(ctx.guild.id)
        question_list = []
        author = ctx.message.author
        embed = discord.Embed()
        embed.add_field(name="Application Setup",
                        value="Time to setup the application questions. It will ask for the question, then the "
                              "context (long explanation) and then for conditions. You can have multiple conditions, "
                              "just separate them with a : To finish, answer FINISH")
        embed.add_field(name="Conditions",
                        value="pv#: point value of the question \n img:requires image to get points \n t>#: text must "
                              "be more than # words to get points.")
        embed.add_field(name="Timeout",
                        value="If you take longer than 5 minutes to answer what is asked, you will need to start over!")
        await ctx.send(embed=embed)
        done = False

        def check(message):
            return message.author == author and message.channel == ctx.channel

        while not done:
            await ctx.send("Please send your Question. you have 5 minutes.")
            try:
                question = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return
            if question.content == "FINISH":
                break

            await ctx.send("Please send that question's context. you have 5 minutes.")
            try:
                context = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return

            await ctx.send("Please send your conditions, separated by a colon. You have 5 minutes. You do not need "
                           "to, just say \"skip\" if not.")
            try:
                conditions = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return
            question_list.append(question.content + ":" + context.content + ":" + conditions.content)

        serv.applicationFormat = question_list
        await ctx.send("Application format has been set up!")
        save_everything()

    @setup.command()
    @commands.has_any_role("admin")
    async def suggestchannel(self, ctx, channel: str):
        serv = get_server(ctx.guild.id)
        if not channel:
            await ctx.send("You didn't send the id, or say \"here\" to use this channel!")
        else:
            if channel.isdigit():
                serv.suggestChannel = int(channel)
                await ctx.send("Successfully set to: " + self.bot.get_channel(int(channel)).name)
            elif channel == "here":
                serv.suggestChannel = ctx.message.channel.id
                await ctx.send("Successfully set to: " + ctx.message.channel.name)
            else:
                await ctx.send("That wasn't an id or here!")
                return
        save_everything()

    @setup.command()
    @commands.has_any_role("admin")
    async def appchannel(self, ctx, channel: str):
        serv = get_server(ctx.guild.id)
        if not channel:
            await ctx.send("You didn't send the id, or say \"here\" to use this channel!")
        else:
            if channel.isdigit():
                serv.appChannel = int(channel)
                await ctx.send("Successfully set to: " + self.bot.get_channel(int(channel)).name)
            elif channel == "here":
                serv.appChannel = ctx.message.channel.id
                await ctx.send("Successfully set to: " + ctx.message.channel.name)
            else:
                await ctx.send("That wasn't an id or here!")
                return
        save_everything()

    @setup.command()
    @commands.has_any_role("admin")
    async def messages(self, ctx, message: str):
        serv = get_server(ctx.guild.id)
        options = ["welcome", "accept", "deny"]

        def check(user):
            return user == ctx.message.author

        if not message or message not in options:
            await ctx.send("You didn't say what message you want to setup, or you didn't say an available one! "
                           "Availiable options: welcome, accept, deny")
            return
        else:
            await ctx.send("Please send the message. You have 5 minutes.")
            try:
                msg = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return

            if message == "welcome":
                serv.importantMessages.update({"welcome": msg})
            elif message == "accept":
                serv.importantMessages.update({"accept": msg})
            elif message == "deny":
                serv.importantMessages.update({"deny": msg})
        save_everything()

    @commands.command(category="Admin", brief="Kick Newcomers", description="Anyone with Newcomer role will be yeeted.")
    @commands.has_any_role("admin")
    async def yeetmembers(self, ctx):
        await ctx.message.delete()
        role = discord.utils.get(ctx.message.guild.roles, name="Newcomer")

        if role is None:
            await ctx.channel.send('There is no "Newcomer" role on this server!')
            return

        for member in role.members:
            await member.send("You have been kicked.")
            await ctx.channel.send(member.id)
            print("working so far")
            await ctx.guild.kick(ctx.guild.get_member(member.id))
            print("kicked")



    @commands.command(category="Admin", brief=" Admin: Start a countdown",
                      description="Enter amount of hours for countdown.")
    @commands.has_any_role("admin")
    async def countdown(self, ctx, arg):
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
        t = t * 60  # t is now num of minutes
        while t > 0:
            hours = int(t / 60)
            minutes = int(t % 60)
            stringToSay = str("Remaining time:\n" + str(hours) + ":" + str(minutes))
            await msg.edit(content=stringToSay)
            await asyncio.sleep(60)
            t -= 1
        await ctx.send("EVENT HAS STARTED")
        await msg.delete()
        rebounding = 0


    @commands.command()
    @commands.has_any_role("admin")
    async def accept(self, ctx):
        welcome = ctx.message.mentions[0]
        embed = discord.Embed(name="You were accepted!")
        embed.add_field(name="You were accepted!",
                        value="Congratulations on being accepted!")
        await welcome.send(embed=embed)
        role = discord.utils.get(ctx.guild.roles, name="Member")
        roledos = discord.utils.get(ctx.guild.roles, name="Applicant")
        await welcome.add_roles(role)
        await welcome.remove_roles(roledos)
        await ctx.message.delete()

    @commands.command(brief="Admin: accept suggestion", description="/acceptsuggestion <messageid> <reason>")
    @commands.has_any_role("admin")
    async def acceptsuggestion(self, ctx, arg1, *, args):
        print(arg1)
        await ctx.message.delete()
        delMessage = await ctx.fetch_message(int(arg1))
        oldSuggestion = delMessage.embeds[0].fields[0].name
        newEmbed = discord.Embed(color=0x17F862)
        newEmbed.add_field(name="Suggestion: " + oldSuggestion + " : accepted!", value="Reason: " + args)
        await delMessage.edit(embed=newEmbed)

    @commands.command(brief="Admin: deny suggestion", description="/denysuggestion <guildId> <reason>")
    @commands.has_any_role("admin")
    async def denysuggestion(self, ctx, arg1, *, args):
        await ctx.message.delete()
        delMessage = await ctx.fetch_message(int(arg1))
        oldSuggestion = delMessage.embeds[0].fields[0].name
        newEmbed = discord.Embed(color=0xEE1B1B)
        newEmbed.add_field(name="Suggestion: " + oldSuggestion + " : denied!", value="Reason: " + args)
        await delMessage.edit(embed=newEmbed)

    async def cog_command_error(self, ctx, error):
        print("error")
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have permission to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing required argument\"{}\"".format(error.param.name))
        else:
            await ctx.send(error)
            traceback.print_exc()

# https://gist.github.com/OneEyedKnight/f0411f9a5e9dea23b96be0bf6dd86d2d
def setup(bot):
    bot.add_cog(AdminCommands(bot))
