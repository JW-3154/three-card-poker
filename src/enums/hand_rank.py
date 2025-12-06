from enum import IntEnum

class HandRank(IntEnum):
    """
    This Enum class defines the ranking of poker hands used in the game.
    """
    HIGH_CARD = 0         
    PAIR = 1              
    FLUSH = 2             
    STRAIGHT = 3          
    THREE_OF_A_KIND = 4   
    STRAIGHT_FLUSH = 5    
    MINI_ROYAL_FLUSH = 6  # Mini Royal Flush, specific to California Poker