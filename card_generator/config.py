from pathlib import Path

# File Paths
COMPONENT_DIR = Path(__file__).parent
ROOT_DIR = COMPONENT_DIR.parent
CARD_ASSETS_DIR = COMPONENT_DIR.parent / 'assets' / 'card_generator'
OUTPUT_DIR = COMPONENT_DIR / 'output'
CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'card_fronts'
CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'card_backs'
DECKS_OUTPUT_DIR = OUTPUT_DIR / 'decks'
DECK_OBJECT_OUTPUT_DIR = OUTPUT_DIR / 'deck_object'
CARD_FRONTS_DECK_IMG = '{j}a_deck.png'
CARD_BACKS_DECK_IMG = '{j}b_deck.png'
CARD_OBJECT_TEMPLATE = CARD_ASSETS_DIR / 'object_templates' / 'card.json'
DECK_OBJECT_TEMPLATE = CARD_ASSETS_DIR / 'object_templates' / 'deck.json'

# URLs
ART_FORM_URL  = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home'
ART_FORM_URL2 = 'https://www.serebii.net/pokemon/art'

# Fonts
FONT_DIR = CARD_ASSETS_DIR / 'fonts'
ORIENTAL_PATH = str(FONT_DIR / 'la_oriental.otf')
BARLOW_PATH = str(FONT_DIR / 'barlow.ttf')

# Colours
DARK_COLOUR = (37, 37, 50)
WHITE_COLOUR = (255, 255, 255)