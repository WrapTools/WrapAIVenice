# prompt_memory_example.py

from WrapAIVenice import VeniceChatPrompt  # adjust import as needed
from secret_loader import load_secret


def print_message_chain(messages):
    print("\n🔗 Conversation History:")
    for i, msg in enumerate(messages):
        role = msg["role"].capitalize()
        content = msg["content"].strip()
        print(f"\n{i+1}. {role}:\n{'-' * 10}\n{content}\n")


def main():
    api_key = load_secret("VENICE_API_KEY")

    # model = "mistral-31-24b"
    model = "llama-3.1-405b"

    chat = VeniceChatPrompt(api_key, model)

    # First question
    q1 = "What's the capital of France?"
    print(f"🟦 Asking: {q1}")
    chat.prompt(q1)
    print(f"🟩 Response: {chat.get_response()}")
    # print(f"\n🧠 Total tokens used: {chat.memory.token_count} / {chat.memory.max_tokens}")

    # Follow-up question
    q2 = "What's one famous museum there?"
    print(f"\n🟦 Asking: {q2}")
    chat.prompt(q2)
    print(f"🟩 Response: {chat.get_response()}")
    # print(f"\n🧠 Total tokens used: {chat.memory.token_count} / {chat.memory.max_tokens}")

    # Follow-up question
    q3 = "What's year was the museum built?"
    print(f"\n🟦 Asking: {q3}")
    chat.prompt(q3)
    print(f"🟩 Response: {chat.get_response()}")
    # print(f"\n🧠 Total tokens used: {chat.memory.token_count} / {chat.memory.max_tokens}")

    # # Show full chat history
    # print_message_chain(chat.memory.message_history)

    # ✅ Show total tokens used
    print(f"\n🧠 Total tokens used: {chat.memory.token_count} / {chat.memory.max_tokens}")

    # Summarize (default and custom)
    summary_default = chat.summarize_memory()
    print(f"\n🧾 Summary (default prompt):\n{summary_default}")

    summary_custom = chat.summarize_memory("Summarize in a concise paragraph.")
    print(f"\n🧾 Summary (custom prompt):\n{summary_custom}")

    # Trim if needed
    print(f"Before trim: {chat.memory.token_count}")
    chat.trim_and_summarize_if_needed()
    print(f"After trim: {chat.memory.token_count}")

    # Show memory again after potential reset
    print("\n🔄 Memory After Summary/Trim:")
    print_message_chain(chat.memory.message_history)


if __name__ == "__main__":
    main()
