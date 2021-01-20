from random import randint
import cogs.admincommands as admin
import discord
from discord.ext import commands
from fuzzywuzzy import fuzz
from mcstatus import MinecraftServer
import asyncio

class Shop:
    def __init__(self, name, inventory_pricing, ownerid):
        self.name = name
        self.inventory = inventory_pricing
        self.ownerid = ownerid


# fluffShop = Shop("Fluffy's Shop",{"test":"1st|1d"}) #example shop
# endShop = Shop("End Shop", {"Elytra": "1|25d", "Shulker Boxes": "1|1db"})



class mCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief = "old shop system, command line style")
    async def makeshopcli(self, ctx, *, args):
        # TODO input validation and error msgs for args

        args = args + "  "  # this is so it picks up the inputs correctly

        # await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
        atpos = args.find("#:")
        number = args[atpos + 2: args.find(" ", atpos)]

        user_inventory = {}
        atpos = args.find("n:")
        name = args[atpos + 2: args.find(" ", atpos)]

        atpos = args.find("#:")
        number = int(args[atpos + 2: args.find(" ", atpos)])
        for i in range(1, number + 1):
            atpos = args.find("i" + str(i) + ":")
            item = args[atpos + 3: args.find(" ", atpos)]
            atpos = args.find("p" + str(i) + ":")
            price = args[atpos + 3: args.find(" ", atpos)]
            user_inventory.update({item: price})
        new_shop = Shop(name, user_inventory, ctx.message.author.id)
        admin.get_server(ctx.guild.id).shopList.append(new_shop)
        admin.save_everything()
        await ctx.send("Shop created!")


    @commands.command(brief = "create a shop. Requires name as argument!")
    async def makeshop(self, ctx, name):
        await ctx.send("Setting up a shop with the name of \"{}\"".format(name))
        await ctx.send("It will ask for item name and price, reply FINISH to end.")
        author = ctx.message.author

        def check(message):
            return message.author == author and message.channel == ctx.channel

        user_inventory = {}
        while True :
            await ctx.send("Please send the item's name. You have 5 minutes.")
            try:
                item = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return
            if item.content == "FINISH":
                break
            await ctx.send("Please send the item's price. You have 5 minutes.")
            try:
                price = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return
            user_inventory.update({item.content: price.content})    
        new_shop = Shop(name, user_inventory, ctx.message.author.id)
        admin.get_server(ctx.guild.id).shopList.append(new_shop)
        admin.save_everything()
        await ctx.send("Shop created, with the name {}.".format(name))
   

    @commands.command(brief="Edit your shops",
                      description="Usage: editshop <shopname> <action> actions: delete, itemedit, itemadd.")
    async def editshop(self, ctx, *args):
        the_shops = admin.get_server(ctx.guild.id).shopList
        if len(args) < 2:  # 0:shopname 1:command 2:itemname 3:price/delete
            await ctx.send("You didn't provide a name and action")
            return
        for s in the_shops:
            print(str(s.ownerid == ctx.message.author.id))
            print(str(s.name))
            print(str(args[0]))
            if s.name == args[0] and s.ownerid == ctx.message.author.id:
                if args[1] == "delete":
                    await ctx.send("Deleted shop: " + s.name)
                    the_shops.remove(s)
                elif args[1] == "itemedit":
                    if len(args) < 4:
                        await ctx.send("You didn't provide enough arguments! <itemname> <updated price, or delete>")
                    else:
                        if args[3] == "delete":
                            if s.inventory.pop(args[2], 'error'):
                                await ctx.send("Couldn't find that item!")
                            else:
                                await ctx.send("Item:" + args[2] + " deleted!")
                        else:
                            if args[2] in s.inventory:
                                s.inventory[args[2]] = args[3]
                                await ctx.send("Price of {} changed to {}!".format(args[2], args[3]))
                            else:
                                await ctx.send("Item not found!")
                elif args[1] == "itemadd":
                    if len(args) < 4:
                        await ctx.send("You didn't provide enough arguments! <itemname>   <price>")
                    else:
                        s.inventory[args[2]] = args[3]
                        await ctx.send("Item added!")
                admin.save_everything()
                return
        await ctx.send("Couldn't find that shop or you don't own it!")

    @commands.command(brief="Check Prices.",
                      description="Usage: /shop itemname. Will throw error if too incorrect spelling.")
    async def shop(self, ctx, *, arg):
        theShops = admin.get_server(ctx.guild.id).shopList
        ad = ["fluffy likes cookies. Please support him by getting cookies."]
        item = arg
        item = item.lower()
        found = []
        if item == "all":
            for shopObject in theShops:
                for key in shopObject.inventory:
                    found.append(shopObject.name + " : " + key + " : " + shopObject.inventory[key])
        else:
            for shopObject in theShops:
                for key in shopObject.inventory:
                    if fuzz.partial_ratio(item.lower(), key.lower()) > 85:
                        found.append(shopObject.name + " : " + key + " : " + shopObject.inventory[key])
        embed = discord.Embed(title="Results:", color=0x0099ff)
        found.sort()
        for i in found:
            embed.add_field(name="------", value=i)
        if not found:
            embed.add_field(name="Error:", value="could not find item. doesn't exist or incorrect spelling.")
        if randint(1, 10) == 1:
            embed.add_field(name="------", value=ad[randint(0, len(ad))])
        await ctx.send(embed=embed)

    @shop.error
    async def shop_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't say what you wanted! \n/shop all\n will show all shops.")

    @commands.command(brief="Server Status", description="See if your Server is up!")  # status
    async def status(self, ctx):
        print("command executed")
        server = MinecraftServer.lookup(admin.get_server(ctx.guild.id).serverAddress)
        try:
            response = server.status()
            embed = discord.Embed(title="The server replied in {0} ms.".format(response.latency), color=0x0099ff)
            embed.add_field(name="Players: {}/{}".format(
            response.players.online,
            response.players.max), value="--------------")
            if response.players.sample != None:
                for player in response.players.sample:
                    embed.add_field(name=player.name,value = "--------------")

            await ctx.send(embed=embed)
            #await ctx.send(
                #"The server has {0} players, and replied in {1} ms.".format(status.players.online, status.latency))
            #await ctx.send(status.players)

        except Exception as e:

            await ctx.send("Sorry, the server is offline, or the ip was setup incorrect! :(")
            await ctx.send(e)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have permission to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing required argument\"{}\"".format(error.param.name))
  

def setup(bot):
    bot.add_cog(mCommands(bot))
