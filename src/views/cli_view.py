from src.views.interfaces.view_protocols import GameView
from src.enums.ui_keys import UIKeys
from string import Template
from time import sleep

class CliView(GameView):
    """
    implementation of a command-line interface view
    """
    
    def __init__(self, message_config: dict[str, str] = None):
        self.message_config = message_config if message_config is not None else {}

    def get_text(self, key: UIKeys | str) -> str:
        """
        Helper method to retrieve the text message corresponding to the given key.
        
        Args:
            key (UIKeys | str): A key from UIKeys enum or a string key.

        Returns:
            str: The corresponding text message.
        """
        key_str: UIKeys | str = key.value if isinstance(key, UIKeys) else str(key)
        return self.message_config.get(key_str, f"[Missing Text for {key_str}]")
    
    def show_message(self, key: UIKeys | str, **kwargs) -> None:
        """
        Display a formatted message to the CLI based on the given key and substitution arguments.
        
        Args:
            key (UIKeys | str): A key from UIKeys enum or a string key.

        """
        template_str = self.get_text(key)
        message = Template(template_str).safe_substitute(**kwargs)
        print(message)
    
    def show_text(self, text: str, str_end: str='\n') -> None:
        """
        Display raw text to the CLI.
        
        Args:
            text (str): The text to display.
            str_end (str, optional): The string appended after the last value,
            default a newline. Defaults to '\n'.
        """
        print(text, end=str_end)
    
    def get_input(self, key: UIKeys | str, **kwargs) -> str:
        """
        Get input from the user with a prompt corresponding to the given key.
        Args:
            key (UIKeys | str): A key from UIKeys enum or a string key.
            **kwargs: Additional keyword arguments for string substitution in the prompt.

        Returns:
            str: The user input.
        """
        template_str = self.get_text(key)
        prompt = Template(template_str).safe_substitute(**kwargs)
        return input(prompt)
                
    def wait(self, seconds: float) -> None:
        sleep(seconds)
        
    def set_message_config(self, new_message_config: dict[str, str]):
        """Hot swap method for the message config

        Args:
            new_message_config (dict[str, str]): The new message configuration to set.
        """
        self.message_config = new_message_config