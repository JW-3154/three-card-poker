from src.services.utils.get_file_path import CONFIG_PATHS
from src.services.utils.config_loader import (
    load_app_controller_config,
    load_game_engine_config,
    load_game_controller_config,
)

class ConfigService:
    def __init__(self):
        self._validate_critical_files()

    def _validate_critical_files(self):
        """Validate the existence of critical configuration files.

        Raises:
            FileNotFoundError: If any critical configuration file is missing.
        """
        missing = []
        for name, path in CONFIG_PATHS.items():
            if not path.exists():
                missing.append(f'{name} ({path})')
        
        if missing:
            # Aggregate all missing files and raise an error at once for easier debugging
            raise FileNotFoundError(f"Critical config files missing: {', '.join(missing)}")

    def get_app_controller_config(self) -> dict:
        
        return load_app_controller_config(CONFIG_PATHS['APP_CONTROLLER_CONFIG'])

    def get_game_engine_config(self) -> dict:
        
        return load_game_engine_config(CONFIG_PATHS['GAME_ENGINE_CONFIG'])

    def get_game_controller_config(self) -> dict:
        
        return load_game_controller_config(CONFIG_PATHS['GAME_CONTROLLER_CONFIG'])