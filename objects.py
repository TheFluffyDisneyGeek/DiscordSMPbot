from typing import List, Optional

class Server:
    def __init__(self, guild_id):
        self.guild_id: int = guild_id
        self.shops: List[Shop] = []
        self.server_address = None
        self.REST_enabled = False
        self.REST_address = None
        self.channels = {}
        self.important_messages = {}
        self.application_format = []

    @classmethod
    def from_dict(cls, values: dict):
        obj = cls.__new__(cls)  # Does not call __init__
        super(Server, obj).__init__()  # Don't forget to call any polymorphic base class initializers
        obj.guild_id = values.get("guild_id")  # if this is not initialized we have a problem...
        obj.shops = [Shop.from_dict(x) for x in values["shops"]]
        obj.server_address = values.get("server_address", None)
        obj.REST_enabled = values.get("REST_enabled", False)
        obj.REST_address = values.get("REST_address", None)
        obj.channels = values.get("channels", {})
        obj.important_messages = values.get("important_messages", {})
        obj.application_format = values.get("application_format", [])
        return obj

    def to_dict(self) -> dict:
        obj = {"guild_id": self.guild_id,
               "shops": [shop.to_dict() for shop in self.shops],
               "server_address": self.server_address,
               "REST_enabled": self.REST_enabled,
               "REST_address": self.REST_address,
               "channels": self.channels,
               "important_messages": self.important_messages,
               "application_format": self.application_format}
        return obj


class Shop:
    def __init__(self, name: str, owner: int):
        self.name = name
        self.owner = owner
        self.notifications_enabled = False
        self.shop_id = name.lower().strip().replace(" ", "_")
        self.items: List[ShopItem] = []

    @classmethod
    def from_dict(cls, values: dict):
        obj = cls.__new__(cls)  # Does not call __init__
        super(Shop, obj).__init__()  # Don't forget to call any polymorphic base class initializers
        obj.name = values.get("name")
        obj.owner = values.get("owner")
        obj.notifications_enabled = values.get("notifications_enabled", False)
        obj.shop_id = values.get("shop_id")
        obj.items = [ShopItem.from_dict(x) for x in values["items"]]
        return obj

    def to_dict(self) -> dict:
        obj = {"name": self.name,
               "owner": self.owner,
               "notifications_enabled": self.notifications_enabled,
               "shop_id": self.shop_id,
               "items": [item.to_dict() for item in self.items]}
        return obj


class ShopItem:
    def __init__(self, item: str, amount: int, price: int, misc_items: bool):
        self.item = item
        self.amount = amount
        self.price = price
        self.restock_notified = True
        self.chest: Optional[Chest] = None
        self.misc_items = misc_items

    @classmethod
    def from_dict(cls, values: dict):
        obj = cls.__new__(cls)  # Does not call __init__
        super(ShopItem, obj).__init__()  # Don't forget to call any polymorphic base class initializers
        obj.item = values.get("item")
        obj.amount = values.get("amount")
        obj.price = values.get("price")
        obj.restock_notified = values.get("restock_notified", True)
        obj.chest = values.get("chest", None)
        obj.misc_items = values.get("misc_items")
        return obj

    def to_dict(self) -> dict:
        obj = {"item": self.item,
               "amount": self.amount,
               "price": self.price,
               "restock_notified": self.restock_notified,
               "chest": self.chest.to_dict() if self.chest is not None else {},
               "misc_items": self.misc_items
               }
        return obj


class Chest:
    def __init__(self, x: int, y: int, z: int, world: str):
        self.x = x
        self.y = y
        self.z = z
        self.world = world

    @classmethod
    def from_dict(cls, values: dict):
        obj = cls.__new__(cls)  # Does not call __init__
        super(Chest, obj).__init__()  # Don't forget to call any polymorphic base class initializers
        obj.x = values.get("x")
        obj.y = values.get("y")
        obj.z = values.get("z")
        obj.world = values.get("world")
        return obj

    def to_dict(self):
        return vars(self)  # nothing special needed as we only store base data in this class
