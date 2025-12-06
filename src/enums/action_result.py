from enum import Enum, auto

class ActionResult(Enum):
    """
    An Enum class that defines various action results for game controller and 
    app controller methods.
    """
    
    CONTINUE = auto()
    INSUFFICIENT_BALANCE = auto()
    TOO_MANY_ANTE_TRIES = auto()
    TOO_MANY_PAIR_PLUS_TRIES = auto()
    # More status codes can be added here as needed