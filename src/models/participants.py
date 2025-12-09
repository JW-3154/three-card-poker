from dataclasses import dataclass
from src.models.card import Card

class Participants:
    def __init__(self):
        self.hand:list[Card | None] = [None] * 3
        self.top = 0
    
    def receive_card(self, card: Card) -> None:
        """Receive a card and add it to the participant's hand.

        Args:
            card (Card): The card to be added to the hand.
        """
        self.hand[self.top] = card
        self.top += 1
        
    def clear_hand(self):
        """
        Clear the participant's hand by resetting the hand buffer cursor.
        """
        self.top = 0

    def sort_hand(self):
        """
        Sort the participant's hand in descending order based on card value.
        """
        self.hand.sort(key=lambda x:x.value, reverse=True)
        

class Dealer(Participants):
    def __init__(self):
        super().__init__()
        
        
@dataclass
class Player(Participants):
    
    balance: int
    ante_bet: int = 0
    pair_plus_bet: int = 0
    play_bet: int = 0
    
    def __post_init__(self): # Magic
        """
        Python Interpreter will call this method after the dataclass's __init__ method
        """
        super().__init__()

    def reset_bets(self):
        """
        Reset all bets to zero.
        """
        self.ante_bet = 0
        self.pair_plus_bet = 0
        self.play_bet = 0