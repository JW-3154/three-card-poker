from src.core.evaluators.standard_evaluator import StandardEvaluator
from src.core.evaluators.standard_evaluator import VirtualHandValues, IsFlush

from src.enums.hand_rank import HandRank

class CaliforniaEvaluator(StandardEvaluator):
    """
    Inherits from StandardEvaluator and implements the California Poker specific hand ranking logic.
    Overrides the evaluate_hand_rank method to include the Mini Royal Flush hand rank.
    """
    def evaluate_hand_rank(self, hand_values: VirtualHandValues, flush: IsFlush) -> HandRank:
        
        assert len(hand_values) == 3, "hand values does not contain exactly 3 values!"
        v0, v1, v2 = hand_values
        assert v0 >= v1 >= v2, "Virtual hand values is not sorted in descending order!"
        assert isinstance(flush, bool), "Flush must be a boolean!"
        
        #Pattern 1: Pair || Three of a kind
        
        is_pair: bool = (v0 == v1) or (v1 == v2)
        if is_pair:
            is_three_of_a_kind: bool = (v0 == v2)
            return HandRank.THREE_OF_A_KIND if is_three_of_a_kind else HandRank.PAIR

        #Pattern 2: Flush || Straight Flush || Mini Royal Flush
        
        is_straight: bool = (v0 - 2 == v2)
        if flush:
            
            if v0 == 14 and is_straight: return HandRank.MINI_ROYAL_FLUSH
            
            return HandRank.STRAIGHT_FLUSH if is_straight else HandRank.FLUSH
        
        #pattern 3: Straight || High Card
        
        return HandRank.STRAIGHT if is_straight else HandRank.HIGH_CARD