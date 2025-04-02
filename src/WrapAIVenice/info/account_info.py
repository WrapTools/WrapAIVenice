# account_info.py

import requests
from pprint import PrettyPrinter
from ..data.constants import API_KEY
import logging

# Logger Configuration
logger = logging.getLogger(__name__)


class VeniceApiKeyInfo:
    def __init__(self):
        pass

    def list_api_keys(self):
        url = "https://api.venice.ai/api/v1/api_keys"
        headers = {"Authorization": f"Bearer {API_KEY}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the JSON data
        data = response.json()

        # Initialize pretty printer
        pp = PrettyPrinter(indent=2)

        # Print both raw and formatted versions
        print("Raw response:")
        print(response.text)

        print("\nFormatted output:")
        pp.pprint(data)

    def list_api_key_rate_limits(self):
        url = "https://api.venice.ai/api/v1/api_keys/rate_limits"

        headers = {"Authorization": f"Bearer {API_KEY}"}

        response = requests.request("GET", url, headers=headers)

        response.raise_for_status()  # Check for HTTP errors

        # Parse the JSON data
        data = response.json()

        # Initialize pretty printer
        pp = PrettyPrinter(indent=2)

        # Print both raw and formatted versions
        print("Raw response:")
        print(response.text)

        print("\nFormatted output:")
        pp.pprint(data)


if __name__ == "__main__":
    api_key_info = VeniceApiKeyInfo()
    api_key_info.list_api_keys()
    api_key_info.list_api_key_rate_limits()


