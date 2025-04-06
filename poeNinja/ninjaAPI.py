class poeNinja:
    def __init__(self):
        from utils.utils import Utils
        self.utils = Utils()

    def get_data(self, league_name):
        urls = {
            "currency": f"https://poe.ninja/api/data/currencyoverview?league={league_name}&type=Currency",
            "div": f"https://poe.ninja/api/data/itemoverview?league={league_name}&type=DivinationCard",
            "uniques": [
                f"https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueMap",
                f"https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueJewel",
                f"https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueFlask",
                f"https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueWeapon",
                f"https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueArmour",
                f"https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueAccessory",
            ],
        }

        self.utils.create_directories("Data", "Uniquedata")
        for key, url in urls.items():
            if isinstance(url, list):
                for sub_url in url:
                    name = self.utils.get_item_name(sub_url)
                    data = self.utils.fetch_url_data(sub_url)
                    self.utils.save_data_to_file(data, f"Uniquedata//{name}.json")
            else:
                name = self.utils.get_item_name(url)
                data = self.utils.fetch_url_data(url)
                self.utils.save_data_to_file(data, f"Data//{name}.json")
