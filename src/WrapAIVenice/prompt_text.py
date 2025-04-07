# prompt_text.py
"""
Client for communicating with the Venice AI API.

Includes:
- `VeniceTextPrompt`: Formats prompts, sets attributes, sends API requests,
  and parses structured responses (response + think).
"""


import requests
import json
from pathlib import Path
import hashlib

import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from .prompt_attributes import PromptAttributes, VeniceParameters
from .utils.markdown import MarkdownToText


class VeniceTextPrompt:
    def __init__(self, api_key, model, base_url="https://api.venice.ai/api/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.parsed_response = None
        self.attributes = PromptAttributes()  # Create an instance of VenicePromptAttributes

    def set_attributes(self, **kwargs):
        """Set attributes dynamically, ensuring venice_parameters is always initialized."""
        for key, value in kwargs.items():
            if hasattr(self.attributes, key):
                if key == "venice_parameters":
                    if isinstance(value, dict):
                        setattr(self.attributes, key, VeniceParameters(**value))
                    elif isinstance(value, VeniceParameters):
                        setattr(self.attributes, key, value)
                else:
                    setattr(self.attributes, key, value)

    def prompt(self, user_prompt, system_prompt="You are a helpful assistant.", messages=None):
        """
        Sends a prompt to the Venice AI API and stores the parsed response.
        Uses VenicePromptAttributes for optional parameters.
        """
        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

        payload = {
            "model": self.model,
            "messages": messages
        }

        # Add attributes from VenicePromptAttributes
        attributes_dict = self.attributes.to_dict()
        for key, value in attributes_dict.items():
            if key == "venice_parameters":
                if value:  # Only add if not empty
                    payload["venice_parameters"] = value
            else:
                payload[key] = value

        #logger.debug("Sending request to Venice API:", json.dumps(payload, indent=4))  # Debugging

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=300
            )

            # Log API response
            logger.debug(f"🔹 API Response Received: Status Code {response.status_code}")
            response_json = response.json()

            if "error" in response_json:
                logger.error(f"❌ API Error: {response_json['error']}")
                return None

            self.parsed_response = self.parse_response(response_json)

            # Add prompt data to parsed response
            self.parsed_response.update({
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "parameters": attributes_dict
            })
            return self.parsed_response

        except requests.exceptions.ReadTimeout:
            logger.error(f"❌ Read Timeout for prompt: {user_prompt}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {e}")
            return None

    # Parce methods
    @staticmethod
    def parse_response(response_json):
        """Parses the API response to extract 'think' and 'response' sections."""
        # content = response_json['choices'][0]['message']['content']
        logger.debug(f"Full response:\n{response_json}")

        content = response_json.get('choices', [{}])[0].get('message', {}).get('content', '')

        if '</think>' in content:
            think_end_index = content.find('</think>')
            parsed_response = {
                'think': content[:think_end_index].strip(),
                'response': content[think_end_index + len('</think>'):].strip()
            }
        else:
            parsed_response = {
                'think': "",
                'response': content.strip()
            }

        parsed_response['think'] = parsed_response['think'].replace('<think>', '').replace('</think>', '')
        parsed_response['response'] = parsed_response['response'].replace('<think>', '').replace('</think>', '')

        # Extract citations if available
        venice_parameters = response_json.get('venice_parameters', {})
        citations = venice_parameters.get('web_search_citations', [])
        parsed_response['citations'] = citations

        parsed_response.update({
            'model': response_json.get('model', 'N/A'),
            'created': response_json.get('created', 'N/A'),
            'usage': response_json.get('usage', {})
        })
        # logger.info(parsed_response)
        return parsed_response

    # Get methods
    def get_usage(self):
        """Returns the usage information from the parsed response."""
        if self.parsed_response:
            return self.parsed_response.get('usage', {})
        return "No parsed response available."

    def get_response(self):
        """Returns the response from the parsed response."""
        if self.parsed_response:
            return self.parsed_response.get('response', "")
        return "No parsed response available."

    def get_think(self):
        """Returns the think section from the parsed response."""
        if self.parsed_response:
            return self.parsed_response.get('think', "")
        return "No parsed response available."

    def get_model(self):
        """Returns the model information from the parsed response."""
        if self.parsed_response:
            return self.parsed_response.get('model', "N/A")
        return "No parsed response available."

    # Save methods
    def save_all(self, file_path):
        """Saves the entire parsed response as a JSON file."""
        if self.parsed_response:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)  # Create directory if not exists
            with open(file_path, "w") as f:
                json.dump(self.parsed_response, f, indent=4)
        else:
            logger.warning("No parsed response available to save.")

    def save_response(self, file_path):
        """Saves the response section to a text file."""
        response = self.get_response()
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        if response:
            with open(file_path, "w") as f:
                f.write(response)
        else:
            logger.warning("No response available to save.")

    def save_text_response(self, md_file_path, output_path):
        """
        Converts a Markdown file to plain text and saves the result.

        Parameters:
        - md_file_path (str): Path to the input Markdown file.
        - output_path (str): Path to save the output plain text file.
        """
        try:
            # Initialize the MarkdownToText handler
            md_handler = MarkdownToText(md_file_path)

            # Extract clean text from the Markdown file
            clean_text = md_handler.extract_clean_text()

            # Save the clean text to the specified output path
            md_handler.save_clean_text(output_path)

            logger.info(f"Clean text response saved to: {output_path}")
        except Exception as e:
            logger.error(f"An error occurred while saving the text response: {e}")

    # Hash methods
    def get_structured_payload_for_hash(
            self, document_id: str, user_prompt: str, system_prompt: str, user_prompt_type: str = "request"
    ) -> dict:
        return {
            "document_id": document_id,
            "system_prompt": system_prompt,
            user_prompt_type: {
                "model": self.model,
                "user_prompt": user_prompt,
                "parameters": self.attributes.to_dict()
            }
        }

    def get_hash(self, structured_payload: dict) -> str:
        return hashlib.sha256(json.dumps(structured_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

