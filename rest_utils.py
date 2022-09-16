import requests
from nbtlib import Compound, Int, String, parse_nbt
from typing import List
from objects import Shop, ShopItem, Server


def strip_namespace(string: str):
    return string.split(":")[1]


def condense_items(items: List[Compound]) -> dict:
    condensed = {}
    for item in items:
        if str(item.get("id")) in condensed:
            condensed[str(item.get("id"))] += int(Int(item.get("Count")))
        else:
            condensed[str(item.get("id"))] = int(Int(item.get("Count")))
    return condensed


def check_stock(server: Server, si: ShopItem):
    chest = si.chest
    r = requests.get(f"http://{server.REST_address}/block",
                     json={'x': chest.x, 'y': chest.y, 'z': chest.z, "world": chest.world})
    print(f"result: {r.text} ")
    compound: Compound = parse_nbt(r.text)
    items = condense_items(compound.get("Items"))
    print(items)
    new_items = {}
    for k in items.keys():
        new_items[strip_namespace(k)] = items[k]

    return new_items.get(si.item, 0), new_items.get("diamond", 0)


def get_stock_amount(si: ShopItem, num: int):
    return int(num / si.amount)
