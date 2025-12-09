from dataclasses import dataclass

@dataclass(frozen=True)
class Card:
    """
    Represents a playing card with a suit, rank, and value.
    """
    suit: str
    rank: str
    value: int