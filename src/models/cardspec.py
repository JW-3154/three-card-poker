"""
This module defines the specifications for playing cards, including suits, ranks, and values.
"""
# Here are the four suits represented by their Unicode characters:
                    #    ♠         ♣        ♥         ♦
SUITS: tuple[str] = ('\u2660', '\u2663','\u2665' ,'\u2666')


# Here are the ranks (pips) of the playing cards:

# The actual ranks of the playing cards
RANKS: tuple[str]  = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')

# The values of the playing cards, which will be used later by the evaluator module to assess hand rankings
VALUES: tuple[int]  = tuple(i for i in range(2, 15))

class Colors:
    """
    These are ANSI escape codes for showing recognizable card colors on terminal
    """
    RED = '\033[91m'
    RESET = '\033[0m'