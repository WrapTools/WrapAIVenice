# account_info.py

import requests
from pprint import PrettyPrinter
import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from ..wv_core import KEY_URL, RATE_LIMIT_API_URL, RATE_LIMIT_MODEL_URL

class VeniceApiKeyInfo:
    def __init__(self, api_key):
        self.api_key = api_key

    def list_api_keys(self):
        url = KEY_URL

        headers = {"Authorization": f"Bearer {self.api_key}"}
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
        url = RATE_LIMIT_API_URL

        headers = {"Authorization": f"Bearer {self.api_key}"}

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

    def get_model_rate_limits(self):
        url = RATE_LIMIT_MODEL_URL

        # payload = {}
        headers = {f"Authorization": f"Bearer {self.api_key}"}

        response = requests.request("GET", url, headers=headers)  # , data=payload

        print(response.text)