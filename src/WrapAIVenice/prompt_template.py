# prompt_template.py
"""
Schema for defining and formatting prompt templates.

Includes:
- `PromptTemplate`: Handles text placeholders, file injection, and prompt hashing.
- `DataclassJSONEncoder`: Serializes dataclass instances to JSON-friendly dicts.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Callable
import hashlib
import copy

import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from .prompt_attributes import VeniceParameters
from .handlers import FILE_HANDLERS


@dataclass
class PromptTemplate:
    program: str  # Associated program
    type: str  # Type/category of the prompt
    name: str  # Unique key for JSON storage
    prompt_text: str  # The actual prompt text
    notes: Optional[str] = None
    default_attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure venice_parameters is only set when explicitly provided."""
        venice_params = copy.deepcopy(self.default_attributes.get('venice_parameters', {}))
        if isinstance(venice_params, dict):
            self.default_attributes['venice_parameters'] = VeniceParameters(**venice_params)

    def get_placeholders(self) -> list:
        """
        Extract placeholders of the format << variable >> from the prompt text.
        Returns a list of placeholder names.
        """
        # return re.findall(r'<<\s*(.*?)\s*>>', self.prompt_text)
        return re.findall(r'<<\s*([\w.-]+)\s*>>', self.prompt_text)

    def get_file_placeholders(self) -> list:
        """
        Extract file placeholders of the format [[ variable ]] from the prompt text.
        Returns a list of placeholder names.
        """
        return re.findall(r'%%\s*(.*?)\s*%%', self.prompt_text)

    def get_formatted_prompt(self, values: Dict[str, str | Path]) -> str:
        """
        Format the prompt text by replacing:
        - `<< variable >>` with text values.
        - `%% file_variable %%` with the **content of a file** (if given a Path or string filename, it reads the file).
        """
        formatted_prompt = self.prompt_text
        missing_keys = []

        # 🔹 Replace << variable >> placeholders
        for key in self.get_placeholders():
            if key in values and isinstance(values[key], str):
                pattern = fr'<<\s*{re.escape(key)}\s*>>'
                formatted_prompt = re.sub(pattern, values[key], formatted_prompt)
            else:
                missing_keys.append(f"<< {key} >>")

        # 🔹 Replace %% file_variable %% placeholders
        for key in self.get_file_placeholders():
            if key in values:
                file_content = None
                file_path = values[key]

                # ✅ Convert string paths to Path objects
                if isinstance(file_path, str):
                    file_path = Path(file_path)

                if isinstance(file_path, Path):  # If it's a Path, read file content
                    # if file_path.exists() and file_path.is_file():
                    #     with file_path.open("r", encoding="utf-8") as f:
                    #         file_content = f.read().strip()
                    ext = file_path.suffix.lower()
                    handler = FILE_HANDLERS.get(ext)

                    if handler:
                        try:
                            file_content = handler(file_path)
                            logger.debug(f"📄 Used handler for {ext}: {file_content[:50]}...")
                        except Exception as e:
                            file_content = f"[Error reading file: {file_path.name}]"
                            logger.error(f"Handler error for {file_path}: {e}")
                    else:
                        file_content = f"[Unsupported file type: {ext}]"
                        logger.debug(f"📄 Loaded file content for {key}: {file_content[:50]}...")
                    # else:
                    #     file_content = f"[ERROR: {file_path.name} not found]"
                elif isinstance(values[key], str):  # If already a string, use as-is
                    file_content = values[key]

                # ✅ Replace placeholder if file content is found
                # if file_content is not None:
                #     pattern = fr'%%\s*{re.escape(key)}\s*%%'
                #     formatted_prompt = re.sub(pattern, file_content, formatted_prompt)
                if file_content is not None:
                    formatted_prompt = formatted_prompt.replace(f"%% {key} %%", file_content)
            else:
                missing_keys.append(f"%% {key} %%")

        if missing_keys:
            logger.warning(f"Missing placeholders: {missing_keys}")

        return formatted_prompt

    def generate_prompt(self, prompt_text: str):
        """
        Updates the prompt with a new prompt_text and extracts placeholders dynamically.
        """
        self.prompt_text = prompt_text
        return self.get_placeholders()

    def load_file_values(self, file_path: Path) -> Dict[str, str]:
        """
        Reads text file content for %% file_variable %% and returns its content.

        Example:
            If the prompt contains `%% disclaimer_text %%` and `file_path` is "disclaimer_text.txt":
            - Reads `disclaimer_text.txt`
            - Returns {"disclaimer_text": "<file contents>"}
        """
        file_values = {}

        # logger.debug(f"🔍 Checking file: {file_path}")  # Log file path

        if file_path.exists() and file_path.is_file():
            placeholder_name = file_path.stem  # Extract filename without extension
            with file_path.open("r", encoding="utf-8") as f:
                file_content = f.read().strip()
                file_values[placeholder_name] = file_content  # Store file contents
                logger.debug(
                    f"📄 Loaded file content for {placeholder_name}: {file_content[:100]}...")  # Log first 100 chars
        else:
            file_values[file_path.stem] = f"[ERROR: {file_path.name} not found]"
            logger.error(f"❌ File not found: {file_path}")

        return file_values

    def get_original_prompt_hash(self) -> str:
        """
        Returns the SHA-256 hash of the original prompt text before placeholders are completed.
        """
        return hashlib.sha256(self.prompt_text.encode('utf-8')).hexdigest()
