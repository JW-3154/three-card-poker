"""
This module defines the specifications for playing cards, including suits, ranks, and values.
"""
# Here are the four suits represented by their Unicode characters:
SUITS: tuple[str] = ('♠', '♣','♥' ,'♦')


# Here are the ranks (pips) of the playing cards:

# The actual ranks of the playing cards
RANKS: tuple[str]  = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')

# The virtual ranks of the player cards,
# which will be used later by the evaluator module to assess hand rankings
VALUES: tuple[int]  = tuple(i for i in range(2, 15))