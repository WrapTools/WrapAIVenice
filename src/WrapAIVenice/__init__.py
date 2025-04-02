# WrapAIVenice/__init__.py

import logging

# Create a logger for your library
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# __all__ = ['']

def some_function():
    logger.debug("This is a debug message from my_library.")

# In use
from .schema_document import DocumentManager
from .utils.markdown import MarkdownToTextFromString
from .prompt_store import PromptManager
from .prompt_attributes import VeniceParameters
from .venice_client import  VeniceTextPrompt, VeniceChatPrompt
from .prompt_template import PromptTemplate

# Superseded
# from .prompt_sum_eval import DocumentSumEvalManager
# from .prompt_summary import DocumentSummaryManager

