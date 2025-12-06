import locale
from src.services.utils.get_file_path import get_locale_dir
from src.services.utils.config_loader import load_messages

class LocaleService:
    """
    Based on system locale settings, manages the current language for the application
    and provides access to localized message configurations and rules file paths.
    Attributes:
        default_lang (str): The default language code to fall back on.
        current_lang_code (str): The currently detected or set language code.
    Methods:
        get_messages_config() -> dict:
            Loads and returns the message configuration for the current language.
        get_rules_file_path() -> str:
            Returns the file path to the rules text file for the current language.
        switch_language(lang_code: str) -> None:
            Switches the current language to the specified language code.
            
    """
    def __init__(self, default_lang: str = "en_US"):
        self.default_lang = default_lang
        self.current_lang_code = self._detect_system_locale()

    def _detect_system_locale(self) -> str:
        
        try:
            locale.setlocale(locale.LC_ALL, '')
            loc = locale.getlocale()[0] # handle Linux and MacOS
        except Exception:
            loc = None
        
        if not loc:
            return self.default_lang
        
        # Handle Windows
        windows_mapping = {
            'Chinese (Simplified)_China': 'zh_CN',
            "Chinese (Simplified)_People's Republic of China": 'zh_CN',
            'Chinese (Traditional)_Taiwan': 'zh_TW',
            'English_United States': 'en_US'
        }
        if loc in windows_mapping:
            return windows_mapping[loc]
        
        if "_" in loc:
            return loc
        
        return self.default_lang

    def get_messages_config(self) -> dict:
        message_path = get_locale_dir(self.current_lang_code) / 'messages.json'
        return load_messages(message_path)

    def get_rules_file_path(self) -> str:
        rules_path = get_locale_dir(self.current_lang_code) / 'rules.txt'
        return str(rules_path)

    def switch_language(self, lang_code: str):
        self.current_lang_code = lang_code