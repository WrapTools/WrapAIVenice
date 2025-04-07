# prompt_chat.py

"""
Client for communicating with the Venice AI API.

Includes:
- `VeniceChatPrompt`: Formats prompts, sets attributes, sends API requests,
  and parses structured responses (response + think + memory).
"""

import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from .prompt_text import VeniceTextPrompt
from .prompt_chat_memory import ConversationMemory
from .info.models import VeniceModels



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
