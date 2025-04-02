# prompt_store.py
"""
Handles storage, loading, and management of prompt templates.

Includes:
- `PromptManager`: Reads/writes prompt templates to JSON with metadata.
"""


import json
from pathlib import Path
from typing import Dict, Optional, Any
import copy
import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from .prompt_attributes import VeniceParameters
from .prompt_template import PromptTemplate


class PromptManager:
    APP_NAME = "CRPrompts"
    DATA_VERSION = "0.1.0"
    FILE_TYPE = "prompts"
    GENERATOR = "direct"

    def __init__(self, file_name: Optional[str] = "prompts.json"):
        """Initialize the manager, load metadata, and prepare prompt storage."""
        self.prompts: Dict[str, PromptTemplate] = {}
        self.file_path = Path(file_name)

        self.header = {
            "app_name": self.APP_NAME,
            "data_version": self.DATA_VERSION,
            "file_type": self.FILE_TYPE,
            "generator": self.GENERATOR,
        }

        # 🔹 Ensure file exists, create if missing
        if not self.file_path.exists():
            logger.info(f"🔹 File '{self.file_path}' not found. Creating a new one.")
            self.save_to_file()  # Save empty structure

        self.load_from_file()  # Load prompts from file

    def load_from_file(self):
        """Loads prompts from a JSON file."""
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)

            # Extract header information
            self.header = json_data.get("header", self.header)

            # Load prompts
            self.prompts = {
                name: PromptTemplate(**data)
                for name, data in json_data.get("data", {}).items()
            }

            logger.info(f"✅ Loaded {len(self.prompts)} prompts from {self.file_path}")

        # except (IOError, json.JSONDecodeError) as err:
        #     logger.error(f"❌ Error loading {self.file_path}: {err}")
        except (IOError, json.JSONDecodeError) as err:
            logger.error(f"❌ Error loading {self.file_path}: {err}")

    def save_to_file(self):
        """Saves prompts and metadata to a JSON file."""
        try:
            json_structure = {
                "header": self.header,
                "data": {name: prompt.__dict__ for name, prompt in self.prompts.items()},
                # "data": {name: asdict(prompt) for name, prompt in self.prompts.items()},

            }

            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(json_structure, f, indent=4)

            logger.info(f"✅ Prompts saved to {self.file_path}")

        except (IOError, TypeError) as err:
            logger.error(f"❌ Error saving to {self.file_path}: {err}")

    def get_full_json(self):
        """Returns the full prompt dataset in JSON format."""
        return {
            "header": self.header,
            "data": {name: prompt.__dict__ for name, prompt in self.prompts.items()},
        }

    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        """Retrieve a prompt by name."""
        return self.prompts.get(name)

    def add_prompt(self, prompt: PromptTemplate):
        """Adds a new prompt to the manager, avoiding unnecessary overwrites."""
        existing_prompt = self.prompts.get(prompt.name)

        if existing_prompt:
            if existing_prompt == prompt:
                logger.info(f"🔹 Prompt '{prompt.name}' already exists with the same content. Skipping.")
                return  # ✅ No need to overwrite identical prompts
            else:
                logger.warning(f"⚠️ Prompt with name '{prompt.name}' exists but is different. Overwriting.")

        self.prompts[prompt.name] = prompt

    def remove_prompt(self, name: str):
        """Removes a prompt by name."""
        if name in self.prompts:
            del self.prompts[name]
            logger.info(f"Removed prompt: {name}")
        else:
            logger.warning(f"Prompt '{name}' not found.")

    def list_prompts(self):
        """Returns a list of all prompt names."""
        return list(self.prompts.keys())

    def create_prompt(self, **kwargs):
        """Creates and adds a new prompt to the manager, ensuring correct structure."""
        valid_keys = {"program", "type", "name", "prompt_text", "notes", "default_attributes"}
        unknown_keys = set(kwargs.keys()) - valid_keys

        if unknown_keys:
            logger.warning(f"Unknown keys in prompt creation: {unknown_keys}")

        try:
            prompt = PromptTemplate(**{k: kwargs[k] for k in valid_keys if k in kwargs})
            self.add_prompt(prompt)
        except TypeError as e:
            logger.error(f"❌ Invalid prompt data: {e}")

    def get_prompt_attributes(self, name: str) -> Dict[str, Any]:
        prompt = self.get_prompt(name)
        attributes = copy.deepcopy(prompt.default_attributes) if prompt else {}

        # Ensure venice_parameters is always included
        if "venice_parameters" not in attributes:
            attributes["venice_parameters"] = VeniceParameters()

        return attributes

