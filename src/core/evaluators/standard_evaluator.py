from src.core.interfaces.evaluator_protocols import GameEvaluator

from src.models.card import Card
from src.enums.hand_rank import HandRank

#typedef / using / type alias / whatever you call it
VirtualHandValues = tuple[int, int, int]
IsFlush           = bool
VirtualHand       = tuple[VirtualHandValues, IsFlush]

class StandardEvaluator(GameEvaluator):
    """
    Implements the standard hand evaluation logic for Three Card Poker.
    """
    def get_formatted_hand(self, hand: list[Card]) -> list[Card]:
        """
        Format the hand for display, 
        providing an interface for the game controller to-
        prevent it from knowing too much logic.
        
        Args:
            hand (list[Card]): A list of Card objects representing a hand.
        Returns:
            list[Card]: A list of Card objects representing the formatted hand.
        """
        values = tuple(card.value for card in hand)
        if values == (14, 3, 2):
            return [hand[1], hand[2], hand[0]]
        return hand
    
    def get_virtual_hand(self, physical_hand: list[Card]) -> VirtualHand:

        """
        Generates a virtual hand representation from a physical hand of cards.
        Args:
            physical_hand (list[Card]): A list of Card objects representing the physical hand.
        Returns:
            VirtualHand: A tuple containing the virtual hand values and
                        a boolean indicating if it's a flush
        """
        
        assert len(physical_hand) == 3, "Physical hand does not contain exactly 3 cards!"
        # Extract card values
        raw_values: VirtualHandValues = tuple(card.value for card in physical_hand)
        
        v0, v1, v2 = raw_values
        assert v0 >= v1 >= v2, "Physical hand is not sorted in descending order!"
        
        # Precompute flush to make data flow more clean
        flush: IsFlush = len({card.suit for card in physical_hand}) == 1

        # Handle A23
        if raw_values == (14, 3, 2):
            adjusted_values: VirtualHandValues = (3, 2, 1)
            adjusted_virtual_hand: VirtualHand = adjusted_values, flush
            return adjusted_virtual_hand
        
        # Handle normal cases
        raw_virtual_hand: VirtualHand = raw_values, flush
        return raw_virtual_hand


    def evaluate_hand_rank(self, hand_values: VirtualHandValues, flush: IsFlush) -> HandRank:
        """
        Evaluates the rank value of a participant's hand
        Args:
            hand_values (VirtualHandValues): _sorted_ virtual hand values.
            flush (IsFlush): a boolean indicating if the hand is a flush.

        Returns:
            HandRank: The rank value of the hand.
        """
        
        assert len(hand_values) == 3, "hand values does not contain exactly 3 values!"
        v0, v1, v2 = hand_values
        assert v0 >= v1 >= v2, "Physical hand is not sorted in descending order!"
        assert isinstance(flush, bool), "Flush must be a boolean!"

        #Pattern 1: Pair || Three of a kind

        is_pair: bool = (v0 == v1) or (v1 == v2)
        if is_pair:
            is_three_of_a_kind: bool = (v0 == v2)
            return HandRank.THREE_OF_A_KIND if is_three_of_a_kind else HandRank.PAIR

        #Pattern 2: Flush || Straight Flush

        is_straight: bool = (v0 - 2 == v2)
        if flush:
            return HandRank.STRAIGHT_FLUSH if is_straight else HandRank.FLUSH

        #pattern 3: Straight || High Card

        return HandRank.STRAIGHT if is_straight else HandRank.HIGH_CARD

    def is_dealer_qualified(
            self,
            dealer_hand_rank_value: HandRank,
            dealer_first_card: int
        ) -> bool:
        """
        Dealer must stand Q high or better to qualify.
        Args:
            dealer_hand_rank_value (HandRank): rank value of the dealer's hand.
            dealer_first_card (int): dealer's highest card value.

        Returns:
            bool: True if the dealer qualifies, False otherwise.
        """
        return dealer_hand_rank_value > HandRank.HIGH_CARD or dealer_first_card >= 12


    def can_player_win(
            self,
            is_dealer_qualified: bool,
            player_hand_rank_value: HandRank,
            dealer_hand_rank_value: HandRank,
            player_hand_values: VirtualHandValues,
            dealer_hand_values: VirtualHandValues
        ) -> bool | None:

        """
        Determines the outcome of the player in the game.
        Returns True if the player wins, False if the player loses, and None if it's a tie.
        Args:
            is_dealer_qualified (bool): Indicates if the dealer qualifies.
            player_hand_rank_value (HandRank): The rank value of the player's hand.
            dealer_hand_rank_value (HandRank): The rank value of the dealer's hand.
            player_hand_values (VirtualHandValues): The sorted virtual hand values of the player.
            dealer_hand_values (VirtualHandValues): The sorted virtual hand values of the dealer.
        Returns:
            bool | None: True if the player wins, False if the player loses, None if it's a tie.
        """
        
        assert isinstance(is_dealer_qualified, bool), "is_dealer_qualified must be a boolean!"
        assert len(player_hand_values) == 3, "Player hand does not have exactly 3 cards!"
        assert len(dealer_hand_values) == 3, "Dealer hand does not have exactly 3 cards!"
        
        
        if not is_dealer_qualified:
            return True

        # Different hand ranks:
        if player_hand_rank_value != dealer_hand_rank_value:
            return player_hand_rank_value > dealer_hand_rank_value
        
        # Same hand rank, special handling for pairs:
        both_are_pair: bool = player_hand_rank_value == HandRank.PAIR
        
        if both_are_pair:
            if player_hand_values[1] != dealer_hand_values[1]:
                # Since the hand values are sorted, only compare the middle card 
                # (e.g., 9,9,2 vs K,8,8)
                return player_hand_values[1] > dealer_hand_values[1]

            # If we reach here, it means the pairs are the same (e.g., 8,8,2 vs K,8,8)
            # The sum trick is used here: 2A + B compare to 2A + C <=> B compare to C
            player_sum :int = sum(player_hand_values)
            dealer_sum :int = sum(dealer_hand_values)
            return None if player_sum == dealer_sum else player_sum > dealer_sum

        # Same hand rank, but not pairs.
        # Compare from the first card, if all three are the same then it's a tie and return None
        for player_card, dealer_card in zip(player_hand_values, dealer_hand_values):
            if player_card > dealer_card:
                return True
            elif player_card < dealer_card:
                return False
        return None