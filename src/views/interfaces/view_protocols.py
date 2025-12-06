from typing import Protocol, Any
from src.enums.ui_keys import UIKeys

class GameView(Protocol):
    """
    Protocol for game view implementations.
    If you want to implement a WebUI or other type of UI, implement this protocol.
    But do not forget a11y, utilize UIKeys to-
    make sure your implementation is accessible for seniors and screen readers.
    """
    def show_message(self, key: UIKeys | str, **kwargs: Any) -> Any:
        ...
    
    def get_input(self, key: UIKeys | str, **kwargs: Any) -> Any:
        ...

    def wait(self, seconds: float) -> Any:
        ...