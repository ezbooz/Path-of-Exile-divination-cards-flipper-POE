import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union
from urllib.request import Request, urlopen


class Utils:
    """Utility class for Path of Exile data processing and file operations."""

    # Constants
    POE_API_LEAGUES_URL = "https://api.pathofexile.com/leagues?type=main"
    GITHUB_VERSION_URL = "https://raw.githubusercontent.com/ezbooz/Path-of-Exile-divination-cards-flipper-POE/main/__version__.py"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    # Special case mappings
    ITEM_NAME_MAPPINGS = {
        "Master Cartographer's Sextant": "Awakened Sextant",
        "Charan's Sword": "Oni-Goroshi",
        "Azyran's Reward": "The Anima Stone"
    }

    def __init__(self):
        pass

    @staticmethod
    def create_directories(*directories: str) -> None:
        """Create multiple directories if they don't exist.

        Args:
            *directories: Variable number of directory paths to create
        """
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def get_item_name(url: str) -> str:
        """Extract item name from poe.ninja API URL.

        Args:
            url: API URL to parse

        Returns:
            Extracted item name
        """
        return url.split("/")[5].split("=")[2]

    @staticmethod
    def fetch_url_data(url: str) -> Union[Dict, List]:
        """Fetch JSON data from a URL.

        Args:
            url: URL to fetch data from

        Returns:
            Parsed JSON data as dictionary or list

        Raises:
            URLError: If the request fails
            ValueError: If JSON parsing fails
        """
        req = Request(url, headers={"User-Agent": Utils.USER_AGENT})
        with urlopen(req) as response:
            return json.loads(response.read().decode())

    @staticmethod
    def save_data_to_file(data: Union[Dict, List], file_path: str) -> None:
        """Save data to a JSON file.

        Args:
            data: Data to save (dict or list)
            file_path: Path to save file
        """
        with open(file_path, "w+", encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

    @staticmethod
    def load_data() -> Tuple[Dict, Dict, Dict]:
        """Load all required data files.

        Returns:
            Tuple containing:
                - Divination card data
                - Currency data
                - Unique items data
        """
        with open("Data\\DivinationCard.json", "r", encoding='utf-8') as f:
            divination_data = json.load(f)

        with open("Data\\Currency.json", "r", encoding='utf-8') as f:
            currency_data = json.load(f)

        unique_items = {}
        for file in os.listdir("Uniquedata"):
            file_path = os.path.join("Uniquedata", file)
            with open(file_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                for item in data["lines"]:
                    unique_items[item["name"]] = item["chaosValue"]

        return divination_data, currency_data, unique_items

    @staticmethod
    def process_card(
            name: str,
            chaos_value: float,
            stack_size: int,
            explicit_modifiers: List[Dict],
            currency: Dict[str, float],
            unique_items: Dict[str, float],
            divination_data: Dict
    ) -> Optional[Dict]:
        """Process divination card data and calculate profit.

        Args:
            name: Card name
            chaos_value: Value in chaos orbs
            stack_size: Number of cards in a full set
            explicit_modifiers: Card reward modifiers
            currency: Currency data dictionary
            unique_items: Unique items data dictionary
            divination_data: Divination card data dictionary

        Returns:
            Dictionary with processed card data or None if processing fails
        """
        if not explicit_modifiers:
            return None

        type_info = explicit_modifiers[0]["text"]
        match = re.match(r"<(.*?)>{(.*?)}", type_info)
        if not match:
            return None

        reward_type, reward_content = match.groups()
        total_cost = chaos_value * stack_size

        # Handle special name cases
        reward_content = Utils._handle_special_names(name, reward_content)

        try:
            if reward_type == "currencyitem":
                return Utils._process_currency_reward(
                    name, reward_content, currency, total_cost, chaos_value, stack_size
                )
            elif reward_type == "uniqueitem":
                return Utils._process_unique_reward(
                    name, reward_content, unique_items, total_cost, chaos_value, stack_size
                )
            else:
                return Utils._process_divination_reward(
                    name, reward_content, divination_data, total_cost, chaos_value, stack_size
                )
        except KeyError as e:
            print(f"KeyError: Item '{e.args[0]}' not found in data for card '{name}'")
            return None

    @staticmethod
    def _process_currency_reward(
            name: str,
            reward_content: str,
            currency: Dict[str, float],
            total_cost: float,
            chaos_value: float,
            stack_size: int
    ) -> Dict:
        """Process currency-type rewards."""
        parts = reward_content.split("x ")
        quantity = float(parts[0]) if len(parts) > 1 else 1.0
        item_name = parts[1] if len(parts) > 1 else parts[0]

        item_name = Utils.ITEM_NAME_MAPPINGS.get(item_name, item_name)
        reward_value = currency[item_name] * quantity

        return Utils._build_card_data(
            name, "Currency", reward_value, total_cost, chaos_value, stack_size
        )

    @staticmethod
    def _process_unique_reward(
            name: str,
            reward_content: str,
            unique_items: Dict[str, float],
            total_cost: float,
            chaos_value: float,
            stack_size: int
    ) -> Dict:
        """Process unique-item rewards."""
        reward_content = Utils.ITEM_NAME_MAPPINGS.get(reward_content, reward_content)
        reward_value = unique_items[reward_content]

        return Utils._build_card_data(
            name, "Unique", reward_value, total_cost, chaos_value, stack_size
        )

    @staticmethod
    def _process_divination_reward(
            name: str,
            reward_content: str,
            divination_data: Dict,
            total_cost: float,
            chaos_value: float,
            stack_size: int
    ) -> Dict:
        """Process divination-card rewards."""
        reward_value = divination_data[reward_content]

        return Utils._build_card_data(
            name, "Divination", reward_value, total_cost, chaos_value, stack_size
        )

    @staticmethod
    def _build_card_data(
            name: str,
            reward_type: str,
            reward_value: float,
            total_cost: float,
            chaos_value: float,
            stack_size: int
    ) -> Dict:
        """Build the card data dictionary."""
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

    @staticmethod
    def _handle_special_names(card_name: str, reward_content: str) -> str:
        """Handle special cases for item names."""
        if card_name == "Azyran's Reward":
            return "The Anima Stone"
        return Utils.ITEM_NAME_MAPPINGS.get(reward_content, reward_content)

    def calculate_highscores(
            self,
            divination_data: Dict,
            currency_data: Dict,
            unique_items: Dict[str, float]
    ) -> Dict[str, Dict]:
        """Calculate profit highscores for divination cards.

        Args:
            divination_data: Divination card data
            currency_data: Currency exchange rates
            unique_items: Unique item prices

        Returns:
            Dictionary of card highscores with profit data
        """
        highscores = {}

        for item in divination_data["lines"]:
            card_data = self.process_card(
                name=item["name"],
                chaos_value=item["chaosValue"],
                stack_size=item.get("stackSize", 1),
                explicit_modifiers=item.get("explicitModifiers", []),
                currency=currency_data,
                unique_items=unique_items,
                divination_data=divination_data,
            )

            if card_data:
                highscores[item["name"]] = card_data

        return highscores

    @staticmethod
    def get_current_leagues() -> List[Dict]:
        """Get list of currently active Path of Exile leagues.

        Returns:
            List of active league dictionaries
        """
        try:
            req = Request(Utils.POE_API_LEAGUES_URL, headers={"User-Agent": Utils.USER_AGENT})
            with urlopen(req) as response:
                leagues = json.loads(response.read().decode("utf-8"))

            current_time = datetime.now(timezone.utc)
            active_leagues = []

            for league in leagues:
                if Utils._is_league_active(league, current_time):
                    active_leagues.append(league)

            return active_leagues

        except Exception as e:
            print(f"Error fetching leagues: {e}")
            return []

    @staticmethod
    def _is_league_active(league: Dict, current_time: datetime) -> bool:
        """Check if a league is currently active."""
        if league.get("endAt"):
            end_date = datetime.fromisoformat(league["endAt"].replace("Z", "+00:00"))
            if end_date < current_time:
                return False

        name = league.get("name", "").lower()
        excluded_terms = {"hardcore", "ssf", "ruthless", "solo self-found"}

        return not any(term in name for term in excluded_terms)

    @staticmethod
    def check_for_updates() -> Optional[str]:
        """Check for available updates on GitHub.

        Returns:
            Remote version string if available, None otherwise
        """
        try:
            req = Request(Utils.GITHUB_VERSION_URL)
            with urlopen(req) as response:
                content = response.read().decode()
                match = re.search(r'__version__ = "(.*?)"', content)
                return match.group(1) if match else None
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None