from src.models.deck import Deck

from src.enums.hand_rank import HandRank
from src.models.card import Card
from src.models.participants import Participants
from src.core.interfaces.evaluator_protocols import GameEvaluator


class GameEngine:
    """
    Game engine coordinating the game flow, managing participants, deck, and evaluation logic.
    Attributes:
        player (Participants): The player participant.
        dealer (Participants): The dealer participant.
        evaluator (GameEvaluator): The game evaluator.
        
        ANTE_BONUS_PAYOUT_RATE_TABLE (dict[int, int]): 
            Payout rates for ante bonus based on hand rank.
            
        PAIR_PLUS_PAYOUT_RATE_TABLE (dict[int, int]): 
            Payout rates for pair plus based on hand rank.
            
        IS_TABLE_LIMIT_ENABLED (bool): Flag to enable or disable table limit enforcement.
        LIMITS_TABLE (dict[str, int]): 
            Constraints and table limits for various bets and conditions.
            
        deck (Deck): The deck of cards used in the game.
    """

    def __init__(
        self,
        player: Participants,
        dealer: Participants,
        evaluator: GameEvaluator,
        ANTE_BONUS_PAYOUT_RATE_TABLE: dict[int, int],
        PAIR_PLUS_PAYOUT_RATE_TABLE: dict[int, int],
        IS_TABLE_LIMIT_ENABLED: bool,
        LIMITS_TABLE: dict[str, int]
        ):
        
        self.__player = player
        self.__dealer = dealer
        self.evaluator = evaluator
        self.ANTE_BONUS_PAYOUT_RATE_TABLE = ANTE_BONUS_PAYOUT_RATE_TABLE
        self.PAIR_PLUS_PAYOUT_RATE_TABLE = PAIR_PLUS_PAYOUT_RATE_TABLE
        self.LIMITS_TABLE = LIMITS_TABLE
        self.IS_TABLE_LIMIT_ENABLED = IS_TABLE_LIMIT_ENABLED 
        self.__deck = Deck()
    
    def reload_game_rules(
        self,
        new_evaluator: GameEvaluator,
        new_ante_table: dict[int, int],
        new_pair_plus_table: dict[int, int],
    ) -> None:
        """
        A interface for AppController to reload game rules and table limits dynamically
        
        Args:
            new_evaluator (GameEvaluator): _new evaluator instance_
            new_ante_table (dict[int, int]): _new ante bonus payout rate table_
            new_pair_plus_table (dict[int, int]): _new pair plus payout rate table_
        """
        
        self.reset_game_state()
        self.evaluator = new_evaluator
        self.ANTE_BONUS_PAYOUT_RATE_TABLE = new_ante_table
        self.PAIR_PLUS_PAYOUT_RATE_TABLE = new_pair_plus_table
    
    def reload_table_limit(
        self,
        new_is_table_limit_enabled: bool,
        new_limits_table: dict[str, int]
        ) -> None:
        """
        A interface for AppController to reload table limit settings dynamically
        
        Args:
            new_is_table_limit_enabled (bool): 
                _new flag to enable or disable table limit enforcement_
            new_limits_table (dict[str, int]): 
                _new constraints and table limits for various bets and conditions_
        """
        
        self.reset_game_state()
        self.IS_TABLE_LIMIT_ENABLED = new_is_table_limit_enabled
        self.LIMITS_TABLE = new_limits_table
        
        
    # Interfaces for game_controller to access player and dealer:
    @property
    def player_balance(self) -> int:
        return self.__player.balance
        
    @property
    def ante_bet(self) -> int:
        return self.__player.ante_bet

    @property
    def pair_plus_bet(self) -> int:
        return self.__player.pair_plus_bet
    
    @property
    def play_bet(self) -> int:
        # In any Three Card Poker rules, play bet equals ante bet
        return self.__player.play_bet
    
    @property
    def has_sufficient_balance(self) -> bool:
        return self.__player.balance >= self.LIMITS_TABLE["game_ends_if_balance_is_less_than"]
    
    @property
    def GAME_ENDING_CONDITION(self) -> int:
        return self.LIMITS_TABLE["game_ends_if_balance_is_less_than"]
    
    @property
    def MIN_ANTE_BET(self) -> int:
        return self.LIMITS_TABLE["min_ante_bet"]
    
    @property
    def MIN_PAIR_PLUS_BET(self) -> int:
        return self.LIMITS_TABLE["min_pair_plus_bet"]
    
    @property
    def max_ante_bet(self) -> int:
        # In any Three Card Poker rules, play bet equals ante bet
        # So the maximum ante bet is half of the balance (reserving the same amount for the play bet)
        if self.LIMITS_TABLE["max_ante_bet"] < 0:
            raise ValueError("max_ante_bet in config can not be negative.")
        
        balance_limit: int = self.__player.balance // 2
        if not self.IS_TABLE_LIMIT_ENABLED:
            return balance_limit
        # This is the configurable table limit
        table_limit: int = self.LIMITS_TABLE["max_ante_bet"] 
        ante_upper_bound = min(balance_limit, table_limit)
        
        return ante_upper_bound
        
    @property
    def max_pair_plus_bet(self) -> int:
        # Here, after placing the ante bet but before the play bet (ante -> pair_plus -> play)
        # Because the play bet equals the ante bet, to place the maximum pair plus bet,
        # at least enough balance must be reserved for the ante/play bets
        if self.LIMITS_TABLE["max_pair_plus_bet"] < 0:
            raise ValueError("max_pair_plus_bet in config can not be negative.")
        
        balance_limit: int = self.__player.balance - self.__player.ante_bet
        if not self.IS_TABLE_LIMIT_ENABLED:
            return balance_limit
        
        table_limit: int = self.LIMITS_TABLE["max_pair_plus_bet"]
        pair_plus_upper_bound = min(balance_limit, table_limit)
        
        return pair_plus_upper_bound
    
    @property
    def player_hand(self) -> list[Card]:
        return self.__player.hand
    
    @property
    def dealer_hand(self) -> list[Card]:
        return self.__dealer.hand
    
    
    # setting player balance and bets
    def add_player_balance(self, amount: int):
        
        if amount < 0:
            raise ValueError("amount can not be negative.")
        self.__player.balance += amount
        
    def deduct_player_balance(self, amount: int):
        
        if amount > self.__player.balance:
            raise ValueError("amount exceeds player's balance.")
        self.__player.balance -= amount

    def place_ante_bet(self, amount: int):
        if not (self.LIMITS_TABLE['min_ante_bet'] <= amount <= self.max_ante_bet):
            raise ValueError(
                "amount is less than minimum ante bet or exceeds maximum ante bet."
            )
        self.deduct_player_balance(amount) # validate first, then change state
        self.__player.ante_bet = amount
        
    def place_pair_plus_bet(self, amount: int): 
        if not (self.LIMITS_TABLE['min_pair_plus_bet'] <= amount <= self.max_pair_plus_bet):
            raise ValueError(
                "amount is less than minimum pair plus bet or exceeds maximum pair plus bet."
            )
        self.deduct_player_balance(amount)
        self.__player.pair_plus_bet = amount
        
    def place_play_bet(self):
        self.__player.play_bet = self.__player.ante_bet
        
        # The value is already valid, no need to validate again
        self.deduct_player_balance(self.__player.play_bet) 
        
    def refund_ante_bet(self):
        self.add_player_balance(self.__player.ante_bet)

    def refund_play_bet(self):
        self.add_player_balance(self.__player.play_bet)

    def refund_pair_plus_bet(self):
        self.add_player_balance(self.__player.pair_plus_bet)
        
    # Dealing and sorting cards
    def shuffle_deck(self):
        self.__deck.shuffle()
    
    def _draw_card_for_participants(self, participants: Participants) -> Card:
        drawn_card = self.__deck.remove_from_deck()
        participants.receive_card(drawn_card)
        # Return the drawn card to the UI, letting the UI decide whether to provide feedback
        return drawn_card
    
    def draw_card_for_player(self) -> Card:
        return self._draw_card_for_participants(self.__player)
    
    def draw_card_for_dealer(self) -> Card:
        return self._draw_card_for_participants(self.__dealer)
        
    def sort_hands(self):
        self.__player.sort_hand()
        self.__dealer.sort_hand()
        
        
    # Evaluation and settlement
    
    def calculate_ante_bonus_payout(self, hand_rank_value: int) -> int:
        
        rate = self.ANTE_BONUS_PAYOUT_RATE_TABLE[hand_rank_value]
        ante_bonus_payout = rate * self.__player.ante_bet
        
        return ante_bonus_payout
    
    def calculate_pair_plus_payout(self, hand_rank_value: int) -> int:
        
        rate = self.PAIR_PLUS_PAYOUT_RATE_TABLE[hand_rank_value]
        pair_plus_payout = rate * self.__player.pair_plus_bet

        return pair_plus_payout
    
    def evaluate(self) -> dict[str, int | bool | None]:
        """
        Calls the evaluator to evaluate both player and dealer hands,
        determines if the dealer qualifies, and decides the outcome for the player.
        Returns:
            dict[str, int | bool | None]: A dictionary containing:
                - 'is_dealer_qualified' (bool): Whether the dealer qualifies.
                - 'player_hand_rank_value' (int): The rank value of the player's hand.
                - 'did_player_win' (bool | None): True if player wins, False if loses, None if tie.
        """
        
        player_hand_values, is_player_flush = self.evaluator.get_virtual_hand(self.__player.hand)
        dealer_hand_values, is_dealer_flush = self.evaluator.get_virtual_hand(self.__dealer.hand)

        player_hand_rank_value = self.evaluator.evaluate_hand_rank(player_hand_values, is_player_flush)
        dealer_hand_rank_value = self.evaluator.evaluate_hand_rank(dealer_hand_values, is_dealer_flush)

        is_dealer_qualified = self.evaluator.is_dealer_qualified(
            dealer_hand_rank_value,
            dealer_hand_values[0]
        )

        did_player_win = self.evaluator.can_player_win(
            is_dealer_qualified,
            player_hand_rank_value,
            dealer_hand_rank_value,
            player_hand_values,
            dealer_hand_values
        )
        
        # Only return the data needed by self.settle
        return { 
            'is_dealer_qualified': is_dealer_qualified,
            'player_hand_rank_value': player_hand_rank_value,
            'did_player_win':did_player_win
        }
    
    def settle(self) -> dict[str, bool | int]:
        
        eval_res = self.evaluate()
        
        is_dealer_qualified = eval_res['is_dealer_qualified']
        player_hand_rank_value = eval_res['player_hand_rank_value']
        
        
        # Determine if the player is eligible for an ante bonus payout based on their hand rank
        ante_bonus_payout: int = 0
        if player_hand_rank_value >= HandRank.STRAIGHT:
            ante_bonus_payout = self.calculate_ante_bonus_payout(player_hand_rank_value)
            self.add_player_balance(ante_bonus_payout)
            
        # Determine if the player is eligible for a pair plus payout based on their hand rank
        had_pair_plus_bet: bool = self.__player.pair_plus_bet >= self.LIMITS_TABLE['min_pair_plus_bet']
        pair_plus_payout: int = 0
        
        if had_pair_plus_bet and player_hand_rank_value >= HandRank.PAIR:
            self.refund_pair_plus_bet()
            pair_plus_payout = self.calculate_pair_plus_payout(player_hand_rank_value)
            self.add_player_balance(pair_plus_payout)

        # Prepare the settlement table to return
        settle_table: dict[str, bool | int] = {
            'is_dealer_qualified':is_dealer_qualified,
            'ante_bonus_payout':ante_bonus_payout,
            'had_pair_plus_bet':had_pair_plus_bet,
            'pair_plus_payout':pair_plus_payout,
        }
        
        # Determine the outcome for the player and adjust balances accordingly
        did_player_win = eval_res['did_player_win']
        winnings: int = 0
        
        match did_player_win:
            
            case False:
                settle_table.update({'outcome':'lose','winnings':winnings}) 
                
            case None:
                
                self.refund_ante_bet()
                self.refund_play_bet()
                
                settle_table.update({'outcome':'push','winnings':winnings}) 
                
            case True:
                
                self.refund_ante_bet()
                self.refund_play_bet()
    
                if not is_dealer_qualified: # Dealer does not qualify, player only wins the ante bet
                    winnings = self.__player.ante_bet
                else:   # Dealer qualifies, player wins both ante and play bets
                    winnings = self.__player.ante_bet + self.__player.play_bet
                    
                settle_table.update({'outcome':'win','winnings':winnings}) 
                
        self.add_player_balance(winnings)
        
        return settle_table
    
    def reset_game_state(self) -> None:

        self.__player.clear_hand()
        self.__dealer.clear_hand()
        
        # Reset player state, including ante bet, pair plus bet, and play bet amounts
        self.__player.reset_bets()