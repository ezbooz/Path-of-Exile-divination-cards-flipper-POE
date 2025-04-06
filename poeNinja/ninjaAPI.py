from typing import Dict, List, Union

from utils.utils import Utils


class PoeNinja:
    """Handles data retrieval from poe.ninja API for various item types."""

    BASE_URL = "https://poe.ninja/api/data/"

    def __init__(self):
        self.utils = Utils()
        self._data_directories = ["Data", "Uniquedata"]

    def get_data(self, league_name: str) -> None:
        """Fetch and save data for the specified league.

        Args:
            league_name: Name of the Path of Exile league to fetch data for
        """
        self._prepare_directories()

        endpoints = self._build_endpoints(league_name)
        self._process_endpoints(endpoints)

    def _prepare_directories(self) -> None:
        """Create required directories for data storage."""
        for directory in self._data_directories:
            self.utils.create_directories(directory)

    def _build_endpoints(self, league_name: str) -> Dict[str, Union[str, List[str]]]:
        """Construct API endpoints for different item types.

        Returns:
            Dictionary mapping item categories to their API endpoints
        """
        return {
            "currency": self._build_url("currencyoverview", league_name, "Currency"),
            "divination": self._build_url(
                "itemoverview", league_name, "DivinationCard"
            ),
            "uniques": [
                self._build_url("itemoverview", league_name, unique_type)
                for unique_type in [
                    "UniqueMap",
                    "UniqueJewel",
                    "UniqueFlask",
                    "UniqueWeapon",
                    "UniqueArmour",
                    "UniqueAccessory",
                ]
            ],
        }

    def _build_url(self, endpoint: str, league_name: str, item_type: str) -> str:
        """Construct a complete API URL.

        Args:
            endpoint: API endpoint name
            league_name: Name of the league
            item_type: Type of items to query

        Returns:
            Complete API URL string
        """
        return f"{self.BASE_URL}{endpoint}?league={league_name}&type={item_type}"

    def _process_endpoints(self, endpoints: Dict[str, Union[str, List[str]]]) -> None:
        """Process all endpoints and save their data.

        Args:
            endpoints: Dictionary of endpoints to process
        """
        for category, url_or_urls in endpoints.items():
            if isinstance(url_or_urls, list):
                self._process_multiple_urls(url_or_urls, "Uniquedata")
            else:
                self._process_single_url(url_or_urls, "Data")

    def _process_single_url(self, url: str, directory: str) -> None:
        """Fetch and save data from a single endpoint.

        Args:
            url: API URL to fetch
            directory: Directory to save the data in
        """
        data = self.utils.fetch_url_data(url)
        filename = self._generate_filename(url, directory)
        self.utils.save_data_to_file(data, filename)

    def _process_multiple_urls(self, urls: List[str], directory: str) -> None:
        """Fetch and save data from multiple endpoints.

        Args:
            urls: List of API URLs to fetch
            directory: Directory to save the data in
        """
        for url in urls:
            self._process_single_url(url, directory)

    def _generate_filename(self, url: str, directory: str) -> str:
        """Generate filename for saving API data.

        Args:
            url: API URL used to generate the filename
            directory: Target directory for the file

        Returns:
            Full file path string
        """
        item_name = self.utils.get_item_name(url)
        return f"{directory}//{item_name}.json"
