# WrapAIVenice/__init__.py

import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# In use
from .schema_document import DocumentManager
from .utils.markdown import MarkdownToTextFromString
from .prompt_store import PromptManager
from .prompt_attributes import VeniceParameters
from .prompt_text import VeniceTextPrompt
from .prompt_chat import VeniceChatPrompt
from .prompt_template import PromptTemplate, VeniceParameters
from .handlers import FILE_HANDLERS
from .wv_core import WEB_SEARCH_MODES, CUSTOM_SYSTEM_PROMPT

__all__ = [
    "DocumentManager",
    "MarkdownToTextFromString",
    "PromptManager",
    "VeniceParameters",
    "VeniceTextPrompt",
    "VeniceChatPrompt",
    "PromptTemplate",
    "FILE_HANDLERS",
    "WEB_SEARCH_MODES",
    "CUSTOM_SYSTEM_PROMPT"
]

# Superseded
# from .prompt_sum_eval import DocumentSumEvalManager
# from .prompt_summary import DocumentSummaryManager

