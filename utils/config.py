import json
import os

def load_config() -> dict:
    """
    Load configuration settings from config.json.
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config
