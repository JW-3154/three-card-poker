from src.enums.ansi_colors import Colors
from src.models.cardspec import SUITS

SPADE, CLUB, HEART, DIAMOND = SUITS

STANDARD_THEME: dict[str, tuple[str, Colors]] = {
    SPADE:   (SPADE,   Colors.RESET),
    CLUB:    (CLUB,    Colors.RESET),
    HEART:   (HEART,   Colors.RED),
    DIAMOND: (DIAMOND, Colors.RED),
}

# default terminal colors
COLOR_BLIND_FRIENDLY_THEME: dict[str, tuple[str, str]] = {
    SPADE: (SPADE, ''),
    CLUB: (CLUB, ''),
    HEART: (HEART, ''),
    DIAMOND: (DIAMOND, ''),
}

SCREEN_READER_THEME: dict[str, tuple[str, str]] = {
    SPADE:   'suit_spade',
    CLUB:    'suit_club',
    HEART:   'suit_heart',
    DIAMOND: 'suit_diamond',
}