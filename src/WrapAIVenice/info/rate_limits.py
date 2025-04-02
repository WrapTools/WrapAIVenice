# rate_limits.py

import requests
import pprint
import logging
import pprint

# 2. Logger Configuration
logger = logging.getLogger(__name__)

from ..data.constants import API_KEY


url = "https://api.venice.ai/api/v1/api_keys/rate_limits/log"

# payload = {}
headers = {f"Authorization": f"Bearer {API_KEY}"}

response = requests.request("GET", url, headers=headers)  # , data=payload

print(response.text)
