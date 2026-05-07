import json
import os

DEFAULT_CONFIG = {
    "llm": {
        "api_url": "https://test-cx-api.giorgioarmani.tech/_v1/llm/proxy/v1/chat/completions",
        "api_key": "sfl-token-llm-very-secret"
    },
    "data_provider": "YAHOO",
    "report_language": "english",
    "news_region": "America"
}

_config = None
_config_path = os.path.join(os.path.dirname(__file__), "../config/config.json")

def load_config():
    global _config
    if _config is not None:
        return _config
    
    if not os.path.exists(_config_path):
        os.makedirs(os.path.dirname(_config_path), exist_ok=True)
        with open(_config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    
    with open(_config_path, "r") as f:
        _config = json.load(f)
    
    return _config

def save_config():
    global _config
    if _config is None:
        load_config()
    with open(_config_path, "w") as f:
        json.dump(_config, f, indent=2)

def get_config():
    return load_config()

def update_config(key, value):
    global _config
    config = load_config()
    
    # Navigate nested keys
    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        current = current[k]
    
    # Validate value
    if keys[-1] == "api_key" and not value.strip():
        raise ValueError("API key cannot be empty")
    
    # Validate data_provider
    if keys[-1] == "data_provider" and value != "YAHOO":
        raise ValueError("Only YAHOO data provider is supported")
    
    # Validate report_language
    valid_languages = {"english", "french", "german", "spanish", "italian", "chinese", "hebrew", "arabic", "russian"}
    if keys[-1] == "report_language" and value not in valid_languages:
        raise ValueError(f"Invalid report language: {value}")
    
    # Validate news_region
    valid_regions = {"America", "Europe", "Asia", "Middle-East"}
    if keys[-1] == "news_region" and value not in valid_regions:
        raise ValueError(f"Invalid news region: {value}")
    
    current[keys[-1]] = value
    _config = config
    save_config()

# Expose config for easy access
config = get_config()