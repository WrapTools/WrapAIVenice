# prompt_attributes.py
"""
Defines configurable parameter structures used in prompt generation.

Includes:
- `PromptAttributes`: General LLM tuning parameters (temperature, max_tokens, etc.)
- `VeniceParameters`: Venice-specific extensions (e.g., web search settings)
"""


from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

import logging

# 2. Logger Configuration
logger = logging.getLogger(__name__)

from .wv_core import WEB_SEARCH_MODES


@dataclass
class VeniceParameters:
    enable_web_search: Optional[str] = None
    include_venice_system_prompt: Optional[bool] = None
    character_slug: Optional[str] = None
    response_format: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate inputs, ensuring they meet expected constraints if provided."""
        if self.enable_web_search is not None and self.enable_web_search not in WEB_SEARCH_MODES:
            raise ValueError(f"enable_web_search must be one of {WEB_SEARCH_MODES}, got '{self.enable_web_search}'")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values to keep output clean."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class PromptAttributes:
    """
    Venice parameters for dictionary:
        enable_web_search: Optional[str] = "off"  # Options: 'auto', 'on', 'off'
        include_venice_system_prompt: Optional[bool] = True
        character_slug: Optional[str] = None
    """

    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    max_completion_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    stream: Optional[bool] = None
    n: Optional[int] = None
    user: Optional[str] = None
    parallel_tool_calls: Optional[bool] = None
    tools: Optional[Any] = None
    tool_choice: Optional[Dict[str, Any]] = None
    stream_options: Optional[Dict[str, Any]] = None

    # venice_parameters: Dict[str, Any] = field(default_factory=dict)
    venice_parameters: VeniceParameters = field(default_factory=VeniceParameters)  # Changed from Dict

    def __post_init__(self):
        if self.temperature is not None and not (0 <= self.temperature <= 2):
            raise ValueError("temperature must be between 0 and 2.")
        if self.top_p is not None and not (0 <= self.top_p <= 1):
            raise ValueError("top_p must be between 0 and 1.")
        if self.frequency_penalty is not None and not (-2 <= self.frequency_penalty <= 2):
            raise ValueError("frequency_penalty must be between -2 and 2.")
        if self.presence_penalty is not None and not (-2 <= self.presence_penalty <= 2):
            raise ValueError("presence_penalty must be between -2 and 2.")

    def to_dict(self) -> Dict[str, Any]:
        """Converts the dataclass to a dictionary, filtering out None values."""
        result = {}
        for k, v in self.__dict__.items():
            if v is not None:
                # Convert nested dataclass to dict
                if k == 'venice_parameters':
                    result[k] = v.to_dict()
                else:
                    result[k] = v
        return result
