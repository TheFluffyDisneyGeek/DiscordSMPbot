import discord
import pickle
from discord.ext import commands
from fuzzywuzzy import fuzz
from random import randint
from mcstatus import MinecraftServer


class Shop:
    def __init__(self, name, inventory_pricing, ownerid):
        self.name = name
        self.inventory = inventory_pricing
        self.ownerid = ownerid



theShops = []
# fluffShop = Shop("Fluffy's Shop",{"test":"1st|1d"}) #example shop
#endShop = Shop("End Shop", {"Elytra": "1|25d", "Shulker Boxes": "1|1db"})


def load_pickled_shops():
    with open("storedVariables/vars.txt", 'rb') as f:
        try:
            stuffs = pickle.load(f)
        except EOFError:
            return []
        return stuffs


def dump_shop_list(sl):
    with open("storedVariables/vars.txt", 'wb') as f:
        pickle.dump(sl, f)


theShops = load_pickled_shops()


class mCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def makeshop(self, ctx, *, args):        
        #TODO input validation and error msgs for args

        args = args + "  "
        # this is so it picks up the inputs correctly

        # await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
        atpos = args.find("#:")
        number = args[atpos + 2: args.find(" ", atpos)]

        user_inventory = {}
        atpos = args.find("n:")
        name = args[atpos + 2: args.find(" ", atpos)]

        atpos = args.find("#:")
        number = int(args[atpos + 2: args.find(" ", atpos)])
        print("\n ---BEGIN DEBUG--- \n")
        print(number)
        for i in range(1, number + 1):
            print(i)
            atpos = args.find("i" + str(i) + ":")
            item = args[atpos + 3: args.find(" ", atpos)]
            atpos = args.find("p" + str(i) + ":")
            price = args[atpos + 3: args.find(" ", atpos)]

            print(item + "\n" + price)
            user_inventory.update({item: price})
        print("----ADDING PROFILE----")
        new_shop = Shop(name, user_inventory,ctx.message.author.id)
        theShops.append(new_shop)
        dump_shop_list(theShops)
        await ctx.send("Shop created!")

    @commands.command(brief="Check Prices.",
                      description="Usage: /shop itemname. Will throw error if incorrect spelling.")
    async def shop(self, ctx, *, arg):
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
                    if fuzz.partial_ratio(item.lower(), key.lower()) > 85:
                        found.append(shopObject.name + " : " + key + " : " + shopObject.inventory[key])
        embed = discord.Embed(title="Results:", color=0x0099ff)
        found.sort()
        for i in found:
            embed.add_field(name="------", value=i)
        if found == []:
            embed.add_field(name="Error:", value="could not find item. doesn't exist or incorrect spelling.")
        if randint(1, 10) == 1:
            embed.add_field(name="------", value=ad[randint(0, len(ad))])
        await ctx.send(embed=embed)

    @shop.error
    async def shop_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't say what you wanted! \n/shop all\n will show all shops.")

    @commands.command(brief="QuackSMP Server Status", description="See if the QuackSMP Server is up")  # status
    async def status(self, ctx):
        server = MinecraftServer.lookup("quacksmp.online")
        try:
            status = server.status()
            await ctx.send(
                "The server has {0} players, and replied in {1} ms.".format(status.players.online, status.latency))
        except:
            off = discord.Game("offline")
            await ctx.send("Sorry, the server is offline :(")
            await self.bot.change_presence(status=discord.Status.dnd, activity=off)
        else:
            game = discord.Game("Now : {0}".format(status.players.online))
            if status.players.online == 0:
                await self.bot.change_presence(status=discord.Status.idle, activity=game)
            else:
                await self.bot.change_presence(activity=game)


def setup(bot):
    bot.add_cog(mCommands(bot))
