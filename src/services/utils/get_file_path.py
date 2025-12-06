from pathlib import Path

"""
Module to provide file paths for configuration and locale files.
"""

BASE_DIR: str = Path(__file__).resolve().parent.parent.parent

CONFIG_PATHS: dict[str, Path] = {
    'GAME_ENGINE_CONFIG' : BASE_DIR / 'config' / 'game_engine_config.json',
    'GAME_CONTROLLER_CONFIG' : BASE_DIR / 'config' / 'game_controller_config.json',
    'APP_CONTROLLER_CONFIG' : BASE_DIR / 'config' / 'app_controller_config.json'
}


LOCALES_BASE_DIR: Path = BASE_DIR / 'config' / 'locales'
DEFAULT_LOCALE = 'en_US'

def get_locale_dir(locale_code: str) -> Path:
    target = LOCALES_BASE_DIR / locale_code
    return target if target.exists() else LOCALES_BASE_DIR / DEFAULT_LOCALE