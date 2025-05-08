import json
import os # For standalone testing

def load_config(config_path="data/config.json"):
    """
    Loads the JSON configuration file.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration as a dictionary, or None if an error occurs.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Configuration loaded successfully from {os.path.abspath(config_path)}")
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {os.path.abspath(config_path)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {os.path.abspath(config_path)}. Check for syntax errors: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading the config from {os.path.abspath(config_path)}: {e}")
        return None

if __name__ == '__main__':
    print("--- Testing Config Loader Standalone ---")
    # Assumes script is in genealogy_analyzer directory for this test
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    
    test_config_path = os.path.join(data_dir, "test_standalone_config.json")
    dummy_config_content = {
        "description": "Test config for config_loader.py standalone execution.",
        "preferred_date_formats": ["%d %b %Y", "%Y"],
        "expected_place_format_structures": ["City, Country"],
    }
    with open(test_config_path, 'w', encoding='utf-8') as f:
        json.dump(dummy_config_content, f, indent=2)
    print(f"Created dummy config file at {test_config_path} for testing.")
        
    config = load_config(test_config_path)
    if config:
        print("Preferred date formats from test config:", config.get("preferred_date_formats"))
    else:
        print(f"Failed to load {test_config_path}")
    print("--- Config Loader Standalone Test Finished ---")