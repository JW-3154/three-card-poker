# === Standard Library ===
import time
import sys

# === Core Domains ===
from src.core.evaluators.california_evaluator import CaliforniaEvaluator
from src.core.evaluators.standard_evaluator import StandardEvaluator
from src.core.game_engine import GameEngine
from src.core.game_controller import GameController

# === Views ===
from src.views.cli_view import CliView

# === Models ===
from src.models.participants import Player, Dealer

# === Services ===
from src.services.config_service import ConfigService
from src.services.locale_service import LocaleService

# === Enums ===
from src.enums.action_result import ActionResult
from src.enums.ui_keys import UIKeys

# I call this "Juarez Cartel Architecture", only El Jefe knows everything

class AppController:  # << El Jefe 🚬😎🥃
    """
    The main application controller that orchestrates the game flow.
    Holds long-lifecycle objects and manages the game loop.
    see: src/core/game_controller.py
    
    Attributes:
        view (CliView): The command-line interface view for user interaction.
            can be swapped out for other view implementations.
            
        conf_svc (ConfigService): Service for loading configuration files.
        loc_svc (LocaleService): Service for loading localization files.
        player (Player): The player model. lifetime matches AppController.
        dealer (Dealer): The dealer model. lifetime matches AppController.
        
        evaluator (GameEvaluator): The game evaluator for hand evaluations,
            lifetime may change on-the-fly.
            
        current_game_rule (str): The current game rule in use (e.g., 'standard', 'california').
        
        game_engine (GameEngine): The core game engine managing game logic.
            it handles deck lifecycle.

        game_ctrl (GameController): The game controller managing game flow.
    """
    
    def __init__(self):
        # Bootstrap
        self.view = CliView()
        try:
            self.conf_svc = ConfigService()
            self.loc_svc = LocaleService()
            self.app_config = self.conf_svc.get_app_controller_config()
            self.ge_config = self.conf_svc.get_game_engine_config()
            self.gc_config = self.conf_svc.get_game_controller_config()

            self.view.set_message_config(self.loc_svc.get_messages_config())
            
        except FileNotFoundError as e:
            self.view.show_text(f"[FATAL ERROR] Startup Failed:\n{str(e)}")
            self.view.wait(5)
            sys.exit(1)

        # Long lifecycle objects
        self.player = Player(self.ge_config['common']['player_initial_balance'])
        self.dealer = Dealer()
        
        # Short lifecycle objects
        self.evaluator = StandardEvaluator()
        self.current_game_rule = 'standard'
        # Long lifecycle objects that hold some short lifecycle objects
        self.game_engine = GameEngine(
            self.player,
            self.dealer,
            self.evaluator,
            self.ge_config[self.current_game_rule]['ante_bonus'],
            self.ge_config[self.current_game_rule]['pair_plus'],
            self.ge_config['common']['is_table_limit_enabled'],
            self.ge_config['common']['limits']
        )

        self.game_ctrl = GameController(self.game_engine, self.view, self.gc_config)
        
    def exit_game(self) -> None:
        self.view.show_message(UIKeys.EXIT_PROMPT)
        self.view.get_input(UIKeys.PRESS_ENTER_TO_EXIT)
        sys.exit(0)
    
    def get_valid_input(self, prompt_key: UIKeys, valid_options: list[str]) -> str:
        """
        A helper method to get valid input from the user-
        based on a prompt and a list of valid options.
        Args:
            prompt_key (UIKeys): The key for the input prompt message.
            valid_options (list[str]): A list of valid input options.
        Returns:
            str: The valid input from the user.
        """
        
        while True:
            user_input = self.view.get_input(prompt_key)
            if user_input in valid_options:
                return user_input
            else:
                self.view.show_message(UIKeys.USER_CHOICE_NOT_IN_OPTIONS_PROMPT)
                
    def interactor(self, key: UIKeys, options: dict[str, callable]) -> None:
        """
        A generic interactor method that handles user choices-
        based on a prompt and a dispatch table of options.
        ActionResult(Enums) from the called functions are handled here.
        
        Args:
            key (UIKeys): The key for the input prompt message.
            options (dict[str, callable]): A dispatch table mapping user choices to functions.
        """
        while True:
            user_choice = self.get_valid_input(key, list(options.keys()))
    
            action_func: callable = options[user_choice]
            ret_value: None | ActionResult = action_func()
            
            match ret_value:
                
                #job done!😄
                case None:
                    break
                
                #not done yet🥲
                case ActionResult.CONTINUE:
                    continue
                
                case ActionResult.INSUFFICIENT_BALANCE:
                    #TODO: Add a refill feature when player balance is insufficient
                    self.exit_game() # temporary solution
                    
                #expected errors:
                case ActionResult.TOO_MANY_ANTE_TRIES:
                    self.view.show_message(UIKeys.TOO_MANY_ANTE_TRIES_PROMPT)
                    continue
                    
                case ActionResult.TOO_MANY_PAIR_PLUS_TRIES:
                    self.view.show_message(UIKeys.TOO_MANY_PAIR_PLUS_TRIES_PROMPT)
                    break
     
        # other case enums:
            
    def read_rules(self) -> ActionResult:
        try:
            with open(self.loc_svc.get_rules_file_path(), mode='r', encoding='UTF-8') as rules:
                while content := rules.readline(): 
                # while(*s++ = *t++); old K&R trick but useful

                    self.view.show_text(content, str_end='')
                    
                    start_time = time.time()
                    self.view.wait(self.app_config['text_rolling_delay_seconds'])
                    waited_time = time.time() - start_time
                    
                    # User suspended the program by Ctrl+Z, 
                    # for better UX (reading experience),
                    # we directly break and return to main menu
                    if waited_time > self.app_config['max_waited_seconds']:
                        break
                    
        except FileNotFoundError:
            self.view.show_message(UIKeys.FILE_NOT_FOUND_ERROR_PROMPT)
            return ActionResult.CONTINUE
        
        return ActionResult.CONTINUE
    
    def switch_rules(self) -> None:
        """
        This func hot swaps game rules, e.g., from standard to california
        1. get user choice
        2. update evaluator
        3. update game engine settings
        4. notify user
        """
        
        # Get user choice
        game_rule_options: dict[str, str] = {
            '1': 'california',
            '2': 'standard'
        }
        
        user_choice: str = self.get_valid_input(
            UIKeys.CHOOSE_GAME_RULE,
            list(game_rule_options.keys())
        )
        
        match user_choice:
            case '1':
                self.evaluator = CaliforniaEvaluator()
            case '2':
                self.evaluator = StandardEvaluator()

        # Update current game rule
        self.current_game_rule = game_rule_options[user_choice]
        
        # Get corresponding settings
        target_config = self.ge_config[self.current_game_rule]
        
        # Reload game engine with new settings
        self.game_engine.reload_game_rules(
            new_evaluator=self.evaluator,
            new_ante_table=target_config['ante_bonus'],
            new_pair_plus_table=target_config['pair_plus']
        )
        
        # Notify user
        game_rule_key_map = {
            'california': UIKeys.CALIFORNIA_MODE,
            'standard': UIKeys.STANDARD_MODE
        }
        
        self.view.show_message(
            UIKeys.GAME_RULE_UPDATED,
            game_rule=self.view.get_text(game_rule_key_map[self.current_game_rule])
        )
        
    def switch_language(self) -> ActionResult:
        """
        A hot swap of language locale
        1. get user choice
        2. update locale service
        3. update view message config
        
        Returns:
            ActionResult.CONTINUE: always
        """
        
        # Get user choice
        language_options: dict[str, str] = {
            '1': 'en_US',
            '2': 'zh_CN',
            '3': 'zh_TW',
        }
        user_choice: str = self.get_valid_input(
            UIKeys.CHOOSE_LANGUAGE_PROMPT,
            list(language_options.keys())
        )
        # Update locale service
        lang_code: str = language_options[user_choice]
        self.loc_svc.switch_language(lang_code)
        
        # Update view message config
        new_messages_config: dict[str, str] = self.loc_svc.get_messages_config()
        self.view.set_message_config(new_messages_config)
        
        return ActionResult.CONTINUE
        
    def run(self) -> None:
        
        # creating dispatch tables 
        first_round_options: dict[str, callable] = {
            '1':self.game_ctrl.first_round,
            '2':self.read_rules,
            '3':self.exit_game,
            '4':self.switch_language,
            '1337':self.game_ctrl._cheat
        }

        pair_plus_round_options = {
            '1':self.game_ctrl.pair_plus_round,
            '2':self.game_ctrl.no_pair_plus,
            '3':self.exit_game
        }

        second_round_options = {
            '1':self.game_ctrl.compare_hand_and_settle,
            '2':self.game_ctrl.fold,
            '3':self.exit_game
        }

        another_game_options = {
            '1':self.game_ctrl.another_game,
            '2':self.switch_rules,
            '3':self.exit_game
        }

        # Main game loop
        self.view.show_message(UIKeys.WELCOMING)
        
        while True:
            try:
                # Game start, place ante bet
                self.interactor(UIKeys.FIRST_ROUND_PROMPT, first_round_options)
                
                # Pair Plus betting round
                if self.game_ctrl.skip_pair_plus: # Insufficient balance for minimum Pair Plus bet, so we skip it
                    self.view.show_message(UIKeys.SKIP_PAIR_PLUS_PROMPT)
                else:
                    self.interactor(UIKeys.PAIR_PLUS_ROUND_PROMPT, pair_plus_round_options) 

                # Second round start, place play bet
                self.game_ctrl.second_round()

                # Whether to compare hands
                self.interactor(UIKeys.SECOND_ROUND_PROMPT, second_round_options)

                # Reset state
                # This method will never raise any error, call 100 times if you are paranoid
                self.game_ctrl.reset_game() 

                # Whether to play another game
                self.interactor(UIKeys.ANOTHER_ROUND_PROMPT, another_game_options)
                
            # Outside interrupts like Ctrl+C or EOF 
            except (EOFError, KeyboardInterrupt):
                self.view.show_message(UIKeys.EXIT_PROMPT)
                break