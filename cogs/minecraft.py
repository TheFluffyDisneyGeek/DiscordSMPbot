import traceback
from random import randint
from typing import Optional

from discord.ui import Item, InputText

import cogs.admincommands as admin
import discord
from discord.ext import commands
from fuzzywuzzy import fuzz
from mcstatus import JavaServer
import asyncio

import objects
from objects import Shop, ShopItem


# fluffShop = Shop("Fluffy's Shop",{"test":"1st|1d"}) #example shop
# endShop = Shop("End Shop", {"Elytra": "1|25d", "Shulker Boxes": "1|1db"})

def get_shops(server: objects.Server, owner: int):
    return [x for x in server.shops if x.owner == owner]


class MinecraftCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''@commands.command(brief="old shop system, command line style")
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
        await ctx.send("Shop created!")'''

    @commands.command(brief="create a shop. Requires name as argument!")
    async def makeshop(self, ctx, name):
        await ctx.send("Setting up a shop with the name of \"{}\"".format(name))
        await ctx.send("It will ask for item name and price, reply FINISH to end.")
        author = ctx.message.author

        def check(message):
            return message.author == author and message.channel == ctx.channel

        new_shop = Shop(name, ctx.message.author.id)

        while True:
            await ctx.send("Please send the item's name. You have 5 minutes.")
            try:
                item = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return
            if item.content == "FINISH":
                break
            await ctx.send("Please send the item's price in the format of <amount>:<price>. You have 5 minutes.")
            try:
                item_price = await self.bot.wait_for("message", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout: please restart this process.")
                return

            new_shop.items.append(
                ShopItem(item.content,
                         int(item_price.content.split(":")[0]),
                         int(item_price.content.split(":")[1]),
                         False
                         ))

        admin.get_server(ctx.guild.id).shops.append(new_shop)
        admin.save_everything()
        await ctx.send("Shop created, with the name {}.".format(name))

    @commands.command(brief="Edit your shops",
                      description="Usage: editshop <shopname>")
    async def editshop(self, ctx, *args):
        the_shops = admin.get_server(ctx.guild.id).shops

        owner = ctx.message.author
        if len(args) < 1:  # 0:shopname 1:command 2:itemname 3:price/delete
            await ctx.send("You didn't provide a name!")
            return
        # TODO delete all setup commands after doing so?

        for s in the_shops:
            if s.name == args[0] and s.owner == owner.id:
                embed = discord.Embed(title="What would you like to do?", color=0xc946d2)
                embed.add_field(name="-------------------------------",
                                value="1️⃣: Edit Shop Name \n 2️⃣: Edit Item \n 3️⃣: Add Item \n 4️⃣: Delete Shop",
                                inline=False)
                embed.add_field(name="-------------------------------", value="You have 1 minute to react.")
                message: discord.Message = await ctx.send(embed=embed)
                await message.add_reaction("1️⃣")
                await message.add_reaction("2️⃣")
                await message.add_reaction("3️⃣")
                await message.add_reaction("4️⃣")

                def react_check(reaction, reactor):
                    return reactor == owner and reaction.emoji in (
                        "1\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
                        "2\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
                        "3\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}",
                        "4\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}")

                def msg_check(message):
                    return message.author == owner and message.channel == ctx.channel

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=react_check)
                except asyncio.TimeoutError:
                    await ctx.send("Timeout: please restart this process.")
                    return
                else:
                    print(reaction.emoji.encode('ascii', 'namereplace'))
                    if reaction.emoji == "1\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}":
                        await ctx.send("Please send the new name, you have 2 minutes.")
                        try:
                            name = await self.bot.wait_for("message", timeout=120.0, check=msg_check)
                        except asyncio.TimeoutError:
                            await ctx.send("Timeout: please restart this process.")
                            return
                        else:
                            s.name = name.content
                            await ctx.send("Successfully changed name!")
                            return

                    elif reaction.emoji == "2\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}":
                        found = []
                        # item_list = []
                        for shop_item in s.items:
                            # TODO format price and amount
                            # TODO change all this to modals and crap
                            found.append(f"{s.name} | {shop_item.item}, {shop_item.amount} : {shop_item.price}")
                            # item_list.append([shop_item.item])
                        embed = discord.Embed(title="Edit which item? You have 5 minutes to respond.", color=0x0099ff)
                        found.sort()
                        for i in found:
                            embed.add_field(name="------", value=i)
                        if not found:
                            await ctx.send("Shop has no items!")
                            return
                        await ctx.send(embed=embed)
                        try:
                            item = await self.bot.wait_for("message", timeout=300.0, check=msg_check)
                        except asyncio.TimeoutError:
                            await ctx.send("Timeout: please restart this process.")
                            return
                        else:
                            if item.content not in [si.item for si in s.items]:
                                await ctx.send("Not a listed item!")
                                return
                            # TODO Actually edit the item lol
                            await ctx.send("send item in format -> <name>:<amount>:<price>")
                            try:
                                new_item = await self.bot.wait_for("message", timeout=300.0, check=msg_check)
                            except asyncio.TimeoutError:
                                await ctx.send("Timeout: please restart this process.")
                                return
                            else:
                                split_item = new_item.content.split(":")
                                # TODO misc item support
                                for si in s.items:
                                    if si.item == item.content:
                                        s.items.remove(si)
                                        break
                                s.items.append(ShopItem(split_item[0], split_item[1], split_item[2], False))
                                await ctx.send("Item edited!")
                                return
                            pass

                            return
                    elif reaction.emoji == "3\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}":
                        await ctx.send("send item in format -> <name>:<amount>:<price>")
                        try:
                            item = await self.bot.wait_for("message", timeout=300.0, check=msg_check)
                        except asyncio.TimeoutError:
                            await ctx.send("Timeout: please restart this process.")
                            return
                        else:
                            split_item = item.content.split(":")
                            # TODO misc item support
                            s.items.append(ShopItem(split_item[0], split_item[1], split_item[2], False))
                            await ctx.send("Item added!")
                            return
                        pass
                    elif reaction.emoji == "4\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}":
                        the_shops.remove(s)
                        await ctx.send("Successfully removed shop!")
                        return
                    else:
                        await ctx.send("Error with reaction")
                        return

                '''if args[1] == "delete":
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
                return'''
        await ctx.send("Couldn't find that shop or you don't own it!")

    @commands.command(brief="Check Prices.",
                      description="Usage: /shop itemname. Will throw error if too incorrect spelling.")
    async def shop(self, ctx, *, arg):
        shops = admin.get_server(ctx.guild.id).shops
        ad = ["fluffy likes cookies. Please support him by getting cookies."]
        item = arg
        item = item.lower()
        found = []
        if item == "all":
            for shop in shops:
                for shop_item in shop.items:
                    # TODO format price and amount
                    found.append(f"{shop.name} | {shop_item.item}, {shop_item.amount} : {shop_item.price}")
        else:
            for shop in shops:
                for shop_item in shop.items:
                    if fuzz.partial_ratio(item.lower(), shop_item.item.lower()) > 85:
                        found.append(f"{shop.name} | {shop_item.item}, {shop_item.amount} : {shop_item.price}")
        embed = discord.Embed(title="Results:", color=0x0099ff)
        found.sort()
        for i in found:
            embed.add_field(name="------", value=i)
        if not found:
            embed.add_field(name="Error:", value="could not find item. doesn't exist or incorrect spelling.")
        if randint(1, 10) == 1:
            embed.add_field(name="------", value=ad[randint(0, len(ad) - 1)])
        await ctx.send(embed=embed)

    @shop.error
    async def shop_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't say what you wanted! \n/shop all\n will show all shops.")

    @commands.command(brief="Server Status", description="See if your Server is up!")  # status
    async def status(self, ctx):
        print("command executed")
        # TODO support bedrock?
        server = JavaServer.lookup(admin.get_server(ctx.guild.id).server_address)
        try:
            response = server.status()
            embed = discord.Embed(title="The server replied in {0} ms.".format(response.latency), color=0x0099ff)
            embed.add_field(name="Players: {}/{}".format(
                response.players.online,
                response.players.max), value="--------------")
            if response.players.sample is not None:
                for player in response.players.sample:
                    embed.add_field(name=player.name, value="--------------")

            await ctx.send(embed=embed)
            # await ctx.send(
            # "The server has {0} players, and replied in {1} ms.".format(status.players.online, status.latency))
            # await ctx.send(status.players)

        except Exception as e:

            await ctx.send("Sorry, the server is offline, or the ip was setup incorrect! :(")
            await ctx.send(e)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have permission to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing required argument\"{}\"".format(error.param.name))
        else:
            await ctx.send(error)
            traceback.print_exc()

    @commands.command(brief="Testing")
    async def test(self, ctx: discord.ext.commands.Context):
        await ctx.send("Select a shop option", view=ShopMenuView(data={}))


def setup(bot):
    bot.add_cog(MinecraftCommands(bot))


# Shop Setup External Logic

class ShopMenuView(discord.ui.View):
    def __init__(self, *items: Item, data=None):
        super().__init__(*items)
        self.data = data

    def get_vars(self):
        self.data['og_message'] = self.message
        self.data['server_obj'] = admin.get_server(self.message.guild.id)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="Timed out.", view=self)

    @discord.ui.button(label="Create Shop", style=discord.ButtonStyle.primary)
    async def create_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_message("WIP")

    @discord.ui.button(label="Edit Shop", style=discord.ButtonStyle.primary)
    async def edit_callback(self, button, interaction: discord.Interaction):
        self.data['shop_owner'] = interaction.user.id
        self.data['guild_id'] = self.message.guild.id
        self.get_vars()
        await interaction.response.edit_message(
            content="Select Shop",
            view=ShopMenuSelectNameView(
                menu_type="edit",
                data=self.data
            ))

    @discord.ui.button(label="Check Shop", style=discord.ButtonStyle.primary)
    async def check_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_message("WIP")


class ShopMenuSelectNameView(discord.ui.View):
    def __init__(self, *items: Item, menu_type: Optional[str] = "", data: dict = None):
        super().__init__(*items)
        self.shop_owner = data['shop_owner']
        self.menu_type = menu_type
        self.server_obj = data['server_obj']
        self.data = data

        if menu_type == "create":
            pass
        elif menu_type == "edit":
            selector = discord.ui.Select(
                placeholder="Select Shop Name",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(
                        label=shop.name
                    ) for shop in get_shops(self.server_obj, self.shop_owner)
                ]
            )

            async def select_callback(interaction: discord.Interaction):
                #  Set up the edit menu
                shop = [x for x in get_shops(self.server_obj, self.shop_owner) if
                        x.name == selector.values[0]][0]
                found = []
                for shop_item in shop.items:
                    found.append(f"{shop.name} | {shop_item.item}, {shop_item.amount} : {shop_item.price}")
                    # item_list.append([shop_item.item])
                embed = discord.Embed(title="Current items", color=0x0099ff)
                found.sort()
                for i in found:
                    embed.add_field(name="".join("- " for _ in range(len(i))), value=i, inline=False)
                if not found:
                    embed.add_field(name="------", value="No items are in this shop.", inline=False)
                self.data['shop'] = shop
                await interaction.response.edit_message(
                    content="",
                    embed=embed,
                    view=ShopEditMenuView(
                        data=data
                    ))

            selector.callback = select_callback
            self.add_item(selector)

        elif menu_type == "check":
            pass


class ShopEditMenuView(discord.ui.View):
    def __init__(self, *items: Item, data: dict = None):
        super().__init__(*items)
        self.data = data

    @discord.ui.button(label="Add Item", style=discord.ButtonStyle.primary)
    async def add_callback(self, button, interaction: discord.Interaction):
        self.data['action'] = "item_add"
        await interaction.response.send_modal(ItemAddEditModal(data=self.data))

    @discord.ui.button(label="Edit Item", style=discord.ButtonStyle.primary)
    async def edit_callback(self, button, interaction: discord.Interaction):
        self.data['action'] = "item_edit"
        await interaction.response.edit_message(content="Edit Item", view=ItemSelectorView(data=self.data))

    @discord.ui.button(label="Delete Item", style=discord.ButtonStyle.red)
    async def delete_item_callback(self, button, interaction: discord.Interaction):
        self.data['action'] = "item_delete"
        await interaction.response.edit_message(content="Delete Item", view=ItemSelectorView(data=self.data))

    @discord.ui.button(label="Delete Shop", style=discord.ButtonStyle.red)
    async def delete_shop_callback(self, button, interaction: discord.Interaction):
        self.data['action'] = "shop_delete"
        # TODO make all the text nice and descriptive
        await interaction.response.edit_message(
            content=f"Please confirm that you want to delete {self.data['shop'].name}",
            embed=None,
            view=ConfirmActionView(data=self.data))


class ItemSelectorView(discord.ui.View):
    def __init__(self, *items: Item, data: dict = None):
        self.data = data
        super().__init__(*items)
        selector = discord.ui.Select(
            placeholder="Select item",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=shop_item.item
                ) for shop_item in data['shop'].items
            ]
        )

        async def select_callback(interaction: discord.Interaction):
            item = selector.values[0]
            item_obj: objects.ShopItem = [x for x in self.data['shop'].items if x.item == item][0]
            self.data['og_item'] = item_obj.item  # so we can still reference if edited
            self.data['item_name'] = item_obj.item
            self.data['item_amount'] = item_obj.amount
            self.data['item_price'] = item_obj.price
            self.data['item_misc'] = 'y' if item_obj.misc_items else 'n'

            if self.data['action'] == 'item_edit':
                await interaction.response.send_modal(ItemAddEditModal(data=self.data))
            elif self.data['action'] == 'item_delete':
                await interaction.response.edit_message(
                    content=f"Please confirm that you want to delete {self.data['og_item']}!",
                    embed=None,
                    view=ConfirmActionView(data=self.data))

        selector.callback = select_callback
        self.add_item(selector)


class ItemAddEditModal(discord.ui.Modal):
    def __init__(self, *children: InputText, title='Editing Item', data: dict = None):
        self.data = data
        super().__init__(*children, title=title)
        self.add_item(InputText(label="Item Name (mc id)", placeholder=data.get('item_name', "")))
        self.add_item(InputText(
            label="Item Amount ", placeholder=data.get('item_amount', "")))  # (i.e. <amount> for x diamonds
        self.add_item(
            InputText(label="Item Price ", placeholder=data.get('item_price', "")))  # (i.e. x for <price> diamonds)
        self.add_item(InputText(
            label="Misc item? <y/n>  ",  # (not one specific item sold)
            placeholder=data.get('item_misc', "")))
        if data['server_obj'].REST_enabled:
            pass  # TODO REST INTEGRATION

    async def callback(self, interaction: discord.Interaction):
        self.data['item_name'] = self.children[0].value
        self.data['item_amount'] = self.children[1].value
        self.data['item_price'] = self.children[2].value
        self.data['item_misc'] = self.children[3].value
        #  TODO VALIDATE & rerun if not validated
        await interaction.response.edit_message(
            content=f"Please confirm! \nitem: {self.data['item_name']} \n"
                    f"price: {self.data['item_amount']} for {self.data['item_price']}"
                    f"\nmisc item: {self.data['item_misc']}",
            embed=None,
            view=ConfirmActionView(data=self.data))


class ConfirmActionView(discord.ui.View):
    def __init__(self, *items: Item, data: dict = None):
        super().__init__(*items)
        self.data = data

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_callback(self, button, interaction: discord.Interaction):
        if self.data['action'] == 'item_add':
            self.data['shop'].items.append(objects.ShopItem(
                self.data['item_name'],
                self.data['item_amount'],
                self.data['item_price'],
                self.data['item_misc'].lower().strip() == 'y'  # sneaky way to get the boolean
            ))
            print(self.data['shop'])
            print([shop for shop in get_shops(self.data['server_obj'], self.data['shop_owner'])])
        elif self.data['action'] == 'item_edit':
            item_obj: objects.ShopItem = [x for x in self.data['shop'].items if x.item == self.data['og_item']][0]
            item_obj.item = self.data['item_name']
            item_obj.amount = self.data['item_amount']
            item_obj.price = self.data['item_price']
            item_obj.misc_items = self.data['item_misc'].lower().strip() == 'y'
        elif self.data['action'] == 'item_delete':
            item_obj: objects.ShopItem = [x for x in self.data['shop'].items if x.item == self.data['og_item']][0]
            self.data['shop'].items.remove(item_obj)
        elif self.data['action'] == 'shop_delete':
            admin.get_server(self.data['guild_id']).shops.remove(self.data['shop'])
        for child in self.children:
            print(child)
            child.disabled = True
        await interaction.response.edit_message(content="Confirmed!", embed=None, view=None)
        print("here!")

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_modal(ItemAddEditModal(data=self.data))
