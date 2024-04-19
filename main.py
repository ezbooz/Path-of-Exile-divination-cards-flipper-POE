import json
import os
import re
import ninjaparse
from collections import OrderedDict


def load_data():
    with open("Data\\DivinationCard.json", "r") as read_file:
        divination_data = json.load(read_file)

    with open("Data\\Currency.json", "r") as read_file:
        currency_data = json.load(read_file)

    unique_items = {}
    for file in os.listdir("Uniquedata"):
        file_loc = os.path.join("Uniquedata", file)
        with open(file_loc, "r") as read_file:
            data = json.load(read_file)
            for item in data["lines"]:
                unique_items[item["name"]] = item["chaosValue"]

    return divination_data, currency_data, unique_items

def process_card(name, chaos_value, stack_size, explicit_modifiers, currency, unique_items, divination_data):
    total_cost = chaos_value * stack_size
    type_info = explicit_modifiers[0]["text"]
    match = re.match("<(.*)>{(.*)}", type_info)
    if match:
        if match.group(1) == "currencyitem":
            reward_type = "Currency"
            items = match.group(2).split("x ")
            if len(items) == 1:
                items.insert(0, "1")
            if items[1] == "Master Cartographer's Sextant":
                items[1] = "Awakened Sextant"
            try:
                reward_value = currency.get(items[1], 0) * float(items[0])
            except KeyError:
                print(f"KeyError: Item '{items[1]}' not found in currency data for card '{name}'")
                return None
        elif match.group(1) == "uniqueitem":
            reward_type = "Unique"
            item_reward = match.group(2)
            if item_reward == "Charan's Sword":
                item_reward = "Oni-Goroshi"
            if name == "Azyran's Reward":
                item_reward = "The Anima Stone"
            try:
                reward_value = unique_items.get(item_reward, 0)
            except KeyError:
                print(f"KeyError: Item '{item_reward}' not found in unique items data for card '{name}'")
                return None
        else:
            reward_type = "Divination"
            item_reward = match.group(2)
            try:
                reward_value = divination_data.get(item_reward, 0)
            except KeyError:
                print(f"KeyError: Item '{item_reward}' not found in divination data for card '{name}'")
                return None
        profit = round((reward_value - total_cost), 2)
        return {
            "Name": name,
            "Type": reward_type,
            "Profit": profit,
            "Cost": chaos_value,
            "Stack": stack_size,
            "Profitpercard": round(profit / stack_size, 2),
            "Total": total_cost,
            "Sellprice": reward_value
        }
    return None

def calculate_highscores(divination_data, currency_data, unique_items):
    highscores = {}
    for item in divination_data["lines"]:
        name = item["name"]
        chaos_value = item["chaosValue"]
        stack_size = item.get("stackSize", 1)
        explicit_modifiers = item.get("explicitModifiers", [])
        card_data = process_card(name, chaos_value, stack_size, explicit_modifiers, currency_data, unique_items, divination_data)
        if card_data:
            highscores[name] = card_data
    return highscores

def print_results(highscores_sorted):
    with open('Data\Currency.json', 'r') as file:
        data = json.load(file)
        for line in data["lines"]:
            if line["currencyTypeName"] == "Divine Orb":
                divine_orb_value = line["receive"]["value"]
               
        
    for item in highscores_sorted:
        print(item["Name"] + " (" + str(int(item["Cost"])) + " c | " + str(round(item["Profit"] / divine_orb_value, 2)) + " d)")
        print("Type: " + str(item["Type"]))
        print("Profit: " + str(int(item["Profit"])) + " c (" + str(round(item["Profit"] / divine_orb_value, 2)) + " d)")
        print("Profit per card: " + str(int(item["Profitpercard"])) + " c (" + str(round(item["Profitpercard"] / divine_orb_value, 2)) + " d)")
        print("Chaos needed: " + str(int(item["Total"])) + " c (" + str(round(item["Total"] / divine_orb_value, 2)) + " d)")
        print("Sell price: " + str(int(item["Sellprice"])) + " c (" + str(round(item["Sellprice"] / divine_orb_value, 2)) + " d)")
        print("Card stack: " + str(item["Stack"]))
        print("-" * 50)
        print("\n")
    print(f"1 div = {int(divine_orb_value)} c")
    input('Press any key to exit...')

def main():
    divination_data, currency_data, unique_items = load_data()
    highscores = calculate_highscores(divination_data, currency_data, unique_items)
    highscores_sorted = sorted(highscores.values(), key=lambda x: x["Profitpercard"])
    print_results(highscores_sorted)

if __name__ == "__main__":
    ninjaparse.ninjaparse()
    main()
