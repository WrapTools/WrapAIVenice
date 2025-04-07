# venice_info_example.py

from WrapAIVenice.info.account_info import VeniceApiKeyInfo
from secret_loader import load_secret


if __name__ == "__main__":
    api_key = load_secret("VENICE_API_KEY_ADMIN")

    api_key_info = VeniceApiKeyInfo(api_key)
    api_key_info.list_api_keys()
    api_key_info.list_api_key_rate_limits()
    api_key_info.get_model_rate_limits()