import json

def _read_config_file(file_path: str) -> dict:
    """
    General function to read a JSON configuration file.

    Args:
        file_path (str): The path to the JSON configuration file.

    Returns:
        dict: The configuration data loaded from the JSON file.
    """
    with open(file_path, mode='r', encoding='UTF-8') as json_file:
        config_data = json.load(json_file)
    return config_data

def load_game_engine_config(file_path: str) -> dict[str, int | bool | dict]:
    """Load the game engine configuration from a JSON file.

    Args:
        file_path (str): The path to the game engine configuration file.

    Returns:
        dict[str, int | bool | dict]: The game engine configuration data.
    """
    data = _read_config_file(file_path)

    # helper: does all dirty job (str key -> int key)
    def _parse_table(table_data):
        return {int(k): v for k, v in table_data.items()}

    return {
        'common': {
            'player_initial_balance': data['player_initial_balance'],
            'is_table_limit_enabled':data['is_table_limit_enabled'],
            'limits': data['limits'],
        },

        'standard': {
            'ante_bonus': _parse_table(data['ante_bonus_payout_rate_table']),
            'pair_plus': _parse_table(data['pair_plus_payout_rate_table'])
        },
        'california': {
            'ante_bonus': _parse_table(data['cal_ante_bonus_payout_rate_table']),
            'pair_plus': _parse_table(data['cal_pair_plus_payout_rate_table'])
        }
    }

def load_messages(file_path: str) -> dict[str, str]:
    return _read_config_file(file_path)

def load_game_controller_config(file_path: str) -> dict[str, int | float]:
    return _read_config_file(file_path)

def load_app_controller_config(file_path: str) -> dict[str, float | dict]:
    return _read_config_file(file_path)