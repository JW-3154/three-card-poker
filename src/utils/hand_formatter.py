from src.models.card import Card

def format_hand(hand: list[Card]) -> list[Card]:
    """
    Format the hand for display, 
    providing an interface for the UI to prevent it from knowing too much or changing logic.
    
    Args:
        hand (list[Card]): A list of Card objects representing a hand.

    Returns:
        list[Card]: A list of Card objects representing the formatted hand.
    """
    values = tuple(card.value for card in hand)
    if values == (14, 3, 2):
        return [hand[1], hand[2], hand[0]]
    return hand