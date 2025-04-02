# venice_client.py
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
from .memory import ConversationMemory
from .info.models import VeniceModels


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

        # # Ensure venice_parameters always exists
        # if not isinstance(self.attributes.venice_parameters, VeniceParameters):
        #     self.attributes.venice_parameters = VeniceParameters()

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
            # "messages": [
            #     {"role": "system", "content": system_prompt},
            #     {"role": "user", "content": user_prompt}
            # ]
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

        # except ReadTimeout:
        #     logger.error(f"❌ Read Timeout for prompt: {user_prompt}")
        #     return None  # Returning None in case of timeout
        # except requests.exceptions.RequestException as e:
        #     logger.error(f"❌ Request failed: {e}")
        #     return None  # Handle other request exceptions (e.g., connection errors)

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


class VeniceChatPrompt:
    def __init__(self, api_key, model, summary_model=None, **kwargs):
        # Compose the original class
        self._venice = VeniceTextPrompt(api_key, model, **kwargs)
        self._summary_model = summary_model

        # Initialize model token manager
        self._models = VeniceModels(api_key)
        self._models.fetch_models()

        model_token_limit = self._models.get_tokens_by_model_name(model)
        if isinstance(model_token_limit, int):
            max_context_tokens = model_token_limit
        else:
            logger.warning(f"Unknown max tokens for model '{model}', defaulting to 8000.")
            max_context_tokens = 8000

        # Memory setup with dynamic token max
        self.memory = ConversationMemory(
            system_prompt=kwargs.get('system_prompt', "You are helpful"),
            max_tokens=max_context_tokens
        )

    # Attribute change methods
    def __getattr__(self, name):
        """Automatically delegate undefined attributes/methods to _venice"""
        return getattr(self._venice, name)

    def set_model(self, model_id):
        """Sets a new model and updates token limit if available."""
        self._venice.model = model_id
        self._ensure_models_loaded()

        model_token_limit = self._models.get_tokens_by_model_name(model_id)
        if isinstance(model_token_limit, int):
            self.memory.max_tokens = model_token_limit
        else:
            logger.warning(f"Unknown max tokens for model '{model_id}', keeping previous value.")

    def _ensure_models_loaded(self):
        if not self._models.models_data:
            self._models.fetch_models()

    # Prompt methods
    def prompt(self, user_prompt, system_prompt=None):
        """Modified prompt with memory management"""
        # Memory handling logic
        if system_prompt:
            self.memory.update_system_prompt(system_prompt)

        self.memory.add_message("user", user_prompt)

        # Reuse parent's execution logic
        response = self._venice.prompt(user_prompt=user_prompt, messages=self.memory.message_history)

        if response:
            self.memory.add_message("assistant", response.get('response', ''))
        return response

    def summarize_memory(self, summary_prompt="Summarize this conversation.", model_override=None, buffer=200):
        """
        Summarizes the current memory using the chat model (or optional override).
        Trims memory to fit within token limits of the selected model.
        """
        summary_model = model_override or self._summary_model or self._venice.model
        messages = self.get_trimmed_messages_for_model(summary_model, summary_prompt, buffer)

        old_model = self._venice.model
        self._venice.model = summary_model
        try:
            response = self._venice.prompt(user_prompt=summary_prompt, messages=messages)
        finally:
            self._venice.model = old_model

        if response:
            return response.get("response", "").strip()
        return "Summary not available."

    def get_trimmed_messages_for_model(self, model, summary_prompt, buffer=200):
        """
        Returns a version of memory + summary_prompt that fits within the given model's token limit.
        """
        self._ensure_models_loaded()
        model_token_limit = self._models.get_tokens_by_model_name(model)
        if not isinstance(model_token_limit, int):
            logger.warning(f"Unknown token limit for model '{model}'. Using current memory limit.")
            model_token_limit = self.memory.max_tokens

        # Estimate token cost of summary prompt
        summary_prompt_tokens = self.memory.calculate_tokens(summary_prompt)
        target_limit = model_token_limit - buffer - summary_prompt_tokens

        # Start with system message
        trimmed = [self.memory.messages[0]]
        current_tokens = self.memory.calculate_tokens(self.memory.messages[0]["content"])

        # Add most recent messages in reverse order until we hit the target
        for msg in reversed(self.memory.messages[1:]):
            msg_tokens = self.memory.calculate_tokens(msg["content"])
            if current_tokens + msg_tokens > target_limit:
                break
            trimmed.insert(1, msg)
            current_tokens += msg_tokens

        # Add the summary prompt
        trimmed.append({"role": "user", "content": summary_prompt})
        logger.info(f"Trimmed messages to {len(trimmed)} to fit {model} with buffer {buffer}")
        return trimmed

    def trim_and_summarize_if_needed(self, summary_prompt="Summarize this conversation.", model_override=None):
        """
        Summarizes and resets memory if nearing token limit.
        """
        if self.memory.token_count > self.memory.max_tokens * 0.8:
            summary = self.summarize_memory(summary_prompt, model_override)
            self.memory.reset_with_summary(summary)

    # Clear memory method
    def clear_memory(self):
        self.memory.reset()
