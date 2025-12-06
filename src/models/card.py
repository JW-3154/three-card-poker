from dataclasses import dataclass
from src.models.cardspec import Colors

@dataclass(frozen=True)
class Card:
    """
    Represents a playing card with a suit, rank, and value.
    """
    suit: str
    rank: str
    value: int

    def __repr__(self) -> str:
        if self.suit in ('\u2665', '\u2666'):
            color = Colors.RED # Hearts and Diamonds are red
        else:
            color = Colors.RESET # Spades and Clubs are depending on terminal support
            
        return f'{color}{self.suit}{self.rank}{Colors.RESET}'