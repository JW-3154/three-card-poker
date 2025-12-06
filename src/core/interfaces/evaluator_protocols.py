from typing import Protocol, Any
from src.enums.hand_rank import HandRank

class GameEvaluator(Protocol):
    """
    A protocol that defines the interface for game evaluators.
    You might be using bitmasks to represent card values and hand rank status,
    so I didn't enforce specific args types here.
    Any class that implements this protocol must provide implementations for the following methods.
    """

    def evaluate_hand_rank(self, *args: Any) -> HandRank:
        """
        Evaluates the rank value of a player's hand
        Returns:
            HandRank: The rank value of the hand.
        """
        ...

    def is_dealer_qualified(self, *args: Any) -> bool:
        """
        Dealer must stand Q high or better to qualify.
        Returns:
            bool: True if the dealer qualifies, False otherwise.
        """
        ...

    def can_player_win(self, *args: Any) -> bool | None:
        
        """
        Determines the outcome of the player in the game.
        Returns:
            bool | None: True if the player wins, False if the player loses, None if it's a tie.
        """
        ...