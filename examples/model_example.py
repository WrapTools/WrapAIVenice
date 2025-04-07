from WrapAIVenice.info.models import VeniceModels
from secret_loader import load_secret

import pprint

# Example usage:
if __name__ == "__main__":
    api_key = load_secret("VENICE_API_KEY")

    venice_models = VeniceModels(api_key)
    venice_models.fetch_models()  # Fetch and store models data

    # Get all model names
    model_names = venice_models.get_model_names()
    print("Model Names:", model_names)

    # Get dictionary of model names and their token counts
    model_tokens_dict = venice_models.get_model_tokens_dict()
    # print("Model Tokens Dictionary:", model_tokens_dict)
    # Create a PrettyPrinter instance
    pp = pprint.PrettyPrinter(indent=4)

    # Print the dictionary in a more readable format
    print("Model Tokens Dictionary:")
    pp.pprint(model_tokens_dict)

    # Get token count for a specific model
    specific_model_name = "deepseek-r1-671b"
    tokens = venice_models.get_tokens_by_model_name(specific_model_name)
    print(f"Available Tokens for {specific_model_name}:", tokens)

    print('All model data')
    pp.pprint(venice_models.models_data)
