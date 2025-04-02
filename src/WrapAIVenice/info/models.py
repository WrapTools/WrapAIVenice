# models.py

import requests
import pprint
import logging

# 2. Logger Configuration
logger = logging.getLogger(__name__)

from ..data.constants import API_KEY


class VeniceModels:
    def __init__(self, api_key, base_url="https://api.venice.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.models_data = []  # To store models data after fetching

    # Fetch method
    def fetch_models(self):
        """Fetches the models from the API and stores them in the instance."""
        url = f"{self.base_url}/models"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_json = response.json()
            self.models_data = response_json.get("data", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            self.models_data = []

    # Get methods
    def get_model_names(self):
        """Returns a list of model names (IDs)."""
        return [model.get("id", "N/A") for model in self.models_data]

    def get_model_tokens_dict(self):
        """Returns a dictionary mapping model names to their available context tokens."""
        return {
            model.get("id", "N/A"): model.get("model_spec", {}).get("availableContextTokens", "N/A")
            for model in self.models_data
        }

    def get_tokens_by_model_name(self, model_name):
        """Returns the available context tokens for a specific model name."""
        for model in self.models_data:
            if model.get("id") == model_name:
                return model.get("model_spec", {}).get("availableContextTokens", "N/A")
        return "Model not found"


def main():
    models = VeniceModels(api_key=API_KEY)
    models.fetch_models()
    # print(models.models_data)
    pprint.pprint(models.models_data)

if __name__ == "__main__":
    main()