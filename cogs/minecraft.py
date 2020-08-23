import discord
import json
from discord.ext import commands
from fuzzywuzzy import fuzz
from random import randint
from mcstatus import MinecraftServer


class Shop:
    def __init__(self, name, inventory_pricing):
        self.name = name
        self.inventory = inventory_pricing


class OwnerProfile:
    def __init__(self, user_id, shops):
        self.user_id = user_id
        self.shops = shops


output_json = {}
theShops = []
# fluffShop = Shop("Fluffy's Shop",{"test":"1st|1d"}) #example shop
endShop = Shop("End Shop", {"Elytra": "1|25d", "Shulker Boxes": "1|1db"})
profiles = []


def dumpshops():
    file = open("storedVariables/vars.txt", "r+")
    file.truncate(0)
    file.close()
    global output_json
    global profiles
    output_json = {}
    tempshop_dict = {}
    print(theShops)
    for op in profiles:
        for s in op.shops:
            tempshop_dict.update({s.name, s.inventory})
        output_json.update({op: tempshop_dict})
    with open("storedVariables/vars.txt", 'w') as f:
        f.write(json.dumps(output_json))
    with open("storedVariables/backup.txt", 'w') as f:
        f.write(json.dumps(output_json))

    '''for s in theShops:
        pickledShops.update({s.name: s.inventory})
    with open("storedVariables/vars.txt", 'w') as f:
        f.write(json.dumps(pickledShops))
    with open("storedVariables/backup.txt", 'w') as f:
        f.write(json.dumps(pickledShops))'''
    print("shops dumped!")


def loadshops():
    with open("storedVariables/vars.txt", 'r') as f:
        input_json = json.loads(f.read())
        for op in input_json:
            owner_shops = []
            for s in op:
                owner_shops.append(Shop(s, input_json.get(op).get(s)))
            profiles.append(OwnerProfile(op, owner_shops))
            for os in owner_shops:
                theShops.append(os)
    print("Shops Loaded!")
    print(theShops)


loadshops()


class mCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def makeshop(self, ctx, *, args):
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
        exists = False
        for op in profiles:
            if op.user_id == str(ctx.message.author.id):
                exists = True
                new_shop = Shop(name, user_inventory)
                op.shops.append(new_shop)
                theShops.append(new_shop)
        if not exists:
            new_shop = Shop(name, user_inventory)
            owner_shops = [new_shop]
            theShops.append(new_shop)
            profiles.append(OwnerProfile(op.user_id, owner_shops))
        theShops.append(Shop(args[0], user_inventory))
        dumpshops()
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
