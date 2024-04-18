import os
import json
from urllib.request import Request, urlopen

def ninjaparse():
    league_name = "Necropolis"
    urls = {
        'currency': f'https://poe.ninja/api/data/currencyoverview?league={league_name}&type=Currency',
        'div': f'https://poe.ninja/api/data/itemoverview?league={league_name}&type=DivinationCard',
        'uniques': [
            f'https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueMap',
            f'https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueJewel',
            f'https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueFlask',
            f'https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueWeapon',
            f'https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueArmour',
            f'https://poe.ninja/api/data/itemoverview?league={league_name}&type=UniqueAccessory'
        ]
    }

    create_directories("Data", "Uniquedata")

    for key, url in urls.items():
        if isinstance(url, list):
            for sub_url in url:
                name = get_item_name(sub_url)
                data = fetch_url_data(sub_url)
                save_data_to_file(data, f"Uniquedata//{name}.json")
        else:
            name = get_item_name(url)
            data = fetch_url_data(url)
            save_data_to_file(data, f"Data//{name}.json")

def create_directories(*directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_item_name(url):
    temp = url.split("/")
    temp = temp[5].split("=")
    return temp[2]

def fetch_url_data(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    web_byte = urlopen(req).read()
    return json.loads(web_byte.decode())

def save_data_to_file(data, file_path):
    with open(file_path, 'w+') as outfile:
        json.dump(data, outfile)

ninjaparse()
