from src.enums.action_result import ActionResult
from src.enums.ui_keys import UIKeys
from src.errors.int_input_not_in_legal_range import IntInputNotInLegalRangeError
from src.utils.hand_formatter import format_hand
from src.core.game_engine import GameEngine
from src.views.interfaces.view_protocols import GameView

class GameController:
    """
    The controller class that manages the game flow between the game engine and the game view.
    """
    def __init__(self, game: GameEngine, view: GameView, config: dict[str, int | float]):
        
        self.game = game
        self.view = view
        self.config = config
        self.__has_cheated = False
    
    def reload_config(self, new_config: dict[str, int | float]):
        self.config = new_config

    @property
    def skip_pair_plus(self) -> bool:
        return self.game.MIN_PAIR_PLUS_BET > self.game.max_pair_plus_bet
    
    def _cheat(self) -> ActionResult:
        """
        It's a cheat function for testing purpose.
        1. Check if player already cheated
        2. If not, set player balance to cheat amount
        3. Notify user
        """
        if self.__has_cheated:
            self.view.show_message(UIKeys.PLAYER_ALREADY_CHEATED)
            return ActionResult.CONTINUE
        
        self.game.add_player_balance(self.config['cheat_amount'] - self.game.player_balance)
        
        self.view.show_message(UIKeys.PLAYER_CHEATED)
        
        self.view.show_message(
            UIKeys.SHOW_PLAYER_BALANCE,
            balance=self.game.player_balance
        )
        
        self.__has_cheated = True
        return ActionResult.CONTINUE
    
    def get_bet_amount(
            self,
            input_prompt: UIKeys,
            success_prompt: UIKeys,
            min_bet: int,
            max_bet: int
            ) -> int | None:
        """
        Helper method to get a valid bet amount from the user within specified range.
        Args:
            input_prompt (UIKeys): The prompt key to ask for bet amount.
            success_prompt (UIKeys): The prompt key to confirm successful bet placement.
            min_bet (int): The minimum allowable bet amount.
            max_bet (int): The maximum allowable bet amount.
        Returns:
            int | None: The valid bet amount entered by the user,
                or None if maximum tries exceeded.
        """
        
        USER_MAX_TRIES: int = self.config['user_max_tries']
        tries = 0
        while True:
            try:
                bet_amount = self.view.get_input(input_prompt, min=min_bet, max=max_bet)
                bet_amount = int(bet_amount)
                if not (min_bet <= bet_amount <= max_bet):
                    raise IntInputNotInLegalRangeError
                
            except (ValueError, IntInputNotInLegalRangeError) as e:
                tries += 1
                if tries >= USER_MAX_TRIES:
                    return None
                if isinstance(e, ValueError):
                    self.view.show_message(UIKeys.MUST_TYPE_INTEGER_ERROR_PROMPT)
                else:
                    self.view.show_message(
                        UIKeys.INT_INPUT_NOT_IN_LEGAL_RANGE_ERROR_PROMPT,
                        min=min_bet,
                        max=max_bet
                    )
                continue

            else:
                self.view.show_message(success_prompt, amount=bet_amount)
                return bet_amount
    
    def first_round(self) -> None | ActionResult:
        if not self.game.has_sufficient_balance:
            
            self.view.show_message(
                UIKeys.INSUFFICIENT_BALANCE_PROMPT,
                limit=self.game.GAME_ENDING_CONDITION
            )
            
            return ActionResult.INSUFFICIENT_BALANCE
            
        self.view.show_message(
            UIKeys.SHOW_PLAYER_BALANCE,
            balance=self.game.player_balance
        )
        
        bet_amount = self.get_bet_amount(
            UIKeys.PLACE_ANTE_PROMPT,
            UIKeys.HAS_PLACED_ANTE_PROMPT,
            self.game.MIN_ANTE_BET,
            self.game.max_ante_bet,
        )
        
        if bet_amount is None: # The user input invalid multiple times, return to main menu
            return ActionResult.TOO_MANY_ANTE_TRIES
        else:
            self.game.place_ante_bet(bet_amount)
        
        self.view.show_message(
            UIKeys.SHOW_PLAYER_BALANCE,
            balance=self.game.player_balance
        )
    
    def pair_plus_round(self) -> None | ActionResult:
        
        bet_amount = self.get_bet_amount(
            UIKeys.PLACE_PAIR_PLUS_PROMPT,
            UIKeys.HAS_PLACED_PAIR_PLUS_PROMPT,
            self.game.MIN_PAIR_PLUS_BET,
            self.game.max_pair_plus_bet,
        )
        
        if bet_amount is None: # The user input invalid multiple times, skip pair plus betting
            return ActionResult.TOO_MANY_PAIR_PLUS_TRIES
        else:
            self.game.place_pair_plus_bet(bet_amount)
            
        self.view.show_message(
            UIKeys.SHOW_PLAYER_BALANCE,
            balance=self.game.player_balance
        )
    
    def no_pair_plus(self) -> None:
        self.view.show_message(UIKeys.NO_PAIR_PLUS_PROMPT)
            
    def second_round(self) -> None:
        self.game.shuffle_deck()
        
        # This is three card poker, each participant draws 3 cards
        # DO NOT TOUCH THIS CONST, OR EVERYTHING COLLAPSES
        THREE_TIMES = 3
        
        for _ in range(THREE_TIMES):
            
            self.view.get_input(UIKeys.DRAW_CARD_PROMPT)
            self.view.wait(self.config['draw_card_delay_seconds'])
            
            drawn_card = self.game.draw_card_for_player()
            self.view.show_message(UIKeys.PLAYER_DREW_CARD_MESSAGE, card=drawn_card)
            
            self.view.wait(self.config['draw_card_delay_seconds'])
            
            drawn_card = self.game.draw_card_for_dealer()

            # If you are interested, feel free to implement a "dealer's card reveal" feature here😈
            # But remember to adjust the UIKeys and locale files accordingly
            self.view.show_message(UIKeys.DEALER_DREW_CARD_MESSAGE) 
            
        self.game.sort_hands()
        
        self.view.show_message(
            UIKeys.SHOW_PLAYER_HAND,
            hand=format_hand(self.game.player_hand)
        )
    
    def compare_hand_and_settle(self) -> None:
        self.game.place_play_bet() # Place play bet
        
        self.view.show_message(
            UIKeys.PLACE_PLAY_BET_PROMPT,
            amount=self.game.play_bet
        )
        
        self.view.show_message(
            UIKeys.SHOW_PLAYER_BALANCE,
            balance=self.game.player_balance
        )
        
        self.view.show_message(
            UIKeys.SHOW_PLAYER_HAND,
            hand=format_hand(self.game.player_hand)
        )
        
        self.view.wait(self.config['reveal_dealer_hand_delay_seconds'])

        self.view.show_message(
            UIKeys.SHOW_DEALER_HAND,
            hand=format_hand(self.game.dealer_hand)
        )
        
        settle_res = self.game.settle()

        if settle_res['ante_bonus_payout'] > 0:
            self.view.show_message(
                UIKeys.WIN_ANTE_BONUS_PROMPT,
                amount=settle_res['ante_bonus_payout']
            )

        if settle_res['had_pair_plus_bet'] and settle_res['pair_plus_payout'] > 0:
            self.view.show_message(
                UIKeys.WIN_PAIR_PLUS_PROMPT,
                amount=settle_res['pair_plus_payout']
            )
        elif settle_res['had_pair_plus_bet']:
            self.view.show_message(UIKeys.HAD_PAIR_PLUS_BET_BUT_NO_PAIR_PLUS)


        match settle_res['outcome']:
            
            case 'lose':
                self.view.show_message(UIKeys.LOSE)

            case 'push':
                self.view.show_message(UIKeys.PUSH)
                
            case 'win':
                
                if not settle_res['is_dealer_qualified']:
                    self.view.show_message(UIKeys.DEALER_NOT_QUALIFIED)

                self.view.show_message(UIKeys.WIN, amount=settle_res['winnings'])

        self.view.show_message(
            UIKeys.SHOW_PLAYER_BALANCE,
            balance=self.game.player_balance
        )
         
         
    def fold(self) -> None:
        self.view.wait(self.config['fold_delay_seconds'])
        
        self.view.show_message(UIKeys.FOLD)
        
        self.view.show_message(
            UIKeys.SHOW_PLAYER_BALANCE,
            balance=self.game.player_balance
        )

    def reset_game(self) -> None:
        self.game.reset_game_state()

    def another_game(self) -> None | ActionResult:
        if not self.game.has_sufficient_balance:
            
            self.view.show_message(
                UIKeys.INSUFFICIENT_BALANCE_PROMPT,
                limit=self.game.GAME_ENDING_CONDITION
            )
            
            return ActionResult.INSUFFICIENT_BALANCE