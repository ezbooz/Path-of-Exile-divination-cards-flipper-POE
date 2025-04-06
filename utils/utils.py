import json
import os
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def create_directories(*directories):
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def get_item_name(url):
        temp = url.split("/")
        temp = temp[5].split("=")
        return temp[2]

    @staticmethod
    def fetch_url_data(url):
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        web_byte = urlopen(req).read()
        return json.loads(web_byte.decode())

    @staticmethod
    def save_data_to_file(data, file_path):
        with open(file_path, "w+") as outfile:
            json.dump(data, outfile)

    @staticmethod
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

    @staticmethod
    def process_card(
        name,
        chaos_value,
        stack_size,
        explicit_modifiers,
        currency,
        unique_items,
        divination_data,
    ):
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
                    print(
                        f"KeyError: Item '{items[1]}' not found in currency data for card '{name}'"
                    )
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
                    print(
                        f"KeyError: Item '{item_reward}' not found in unique items data for card '{name}'"
                    )
                    return None
            else:
                reward_type = "Divination"
                item_reward = match.group(2)
                try:
                    reward_value = divination_data.get(item_reward, 0)
                except KeyError:
                    print(
                        f"KeyError: Item '{item_reward}' not found in divination data for card '{name}'"
                    )
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
                "Sellprice": reward_value,
            }
        return None

    def calculate_highscores(self, divination_data, currency_data, unique_items):
        highscores = {}
        for item in divination_data["lines"]:
            name = item["name"]
            chaos_value = item["chaosValue"]
            stack_size = item.get("stackSize", 1)
            explicit_modifiers = item.get("explicitModifiers", [])
            card_data = self.process_card(
                name,
                chaos_value,
                stack_size,
                explicit_modifiers,
                currency_data,
                unique_items,
                divination_data,
            )
            if card_data:
                highscores[name] = card_data
        return highscores

    @staticmethod
    def get_current_leagues():
        url = "https://api.pathofexile.com/leagues?type=main"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        req = Request(url, headers=headers)

        with urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

        current_time = datetime.now(timezone.utc)
        active_leagues = []

        for league in data:
            end_at = league.get("endAt")
            if end_at is not None:
                end_date = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
                if end_date < current_time:
                    continue

            name = league.get("name", "").lower()
            if any(
                word in name
                for word in ["hardcore", "ssf", "ruthless", "solo self-found"]
            ):
                continue

            active_leagues.append(league)

        return active_leagues

    @staticmethod
    def check_for_updates():
        try:
            url = "https://raw.githubusercontent.com/ezbooz/Path-of-Exile-divination-cards-flipper-POE/main/__version__.py"
            req = Request(url)
            web_byte = urlopen(req).read()
            remote_version = re.search(
                r'__version__ = "(.*?)"', web_byte.decode()
            ).group(1)
            return remote_version
        except Exception:
            return None
