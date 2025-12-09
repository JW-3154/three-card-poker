from src.models.card import Card
from src.models.cardspec import SUITS, RANKS, VALUES
import random

class Deck:
    """
    Container class of cards
    """
    def __init__(self):
        self.top = 0
        self.cards: list[Card] = []
        for pips in range(13):
            for suit in range(4):
                each_card = Card(SUITS[suit] , RANKS[pips] , VALUES[pips])
                self.cards.append(each_card)

    def __repr__(self) -> str:
        return f'Deck(There are: {len(self.cards)} cards)\ncards: {self.cards}'

    def shuffle(self):
        random.shuffle(self.cards)
        
    def remove_from_deck(self) -> Card:
        """
        This method will be called by game engine when dealing cards to participants.
        Returns:
            Card: A card object that was removed(semantically, not actually removed) from the deck.
        """
        
        card = self.cards[self.top]
        self.top += 1
        return card

    def janitor(self) -> None:
        """
        Reset cursor to the top of the deck.
        """
        self.top = 0