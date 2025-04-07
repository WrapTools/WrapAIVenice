# token_char.py

import tiktoken
import logging

# Logger Configuration
logger = logging.getLogger(__name__)


def count_characters_and_tokens(text, model='gpt-3.5-turbo'):
    """Returns the character count and token count of the input text."""
    # Character count
    char_count = len(text)

    # Token count using tiktoken
    try:
        # Attempt to get encoding for the specified model
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to a default encoding if model-specific encoding is unavailable
        logger.error(f"Model '{model}' not found. Using 'gpt-3.5-turbo' encoding as a fallback.")
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    token_count = len(encoding.encode(text))
    return char_count, token_count

