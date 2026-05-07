"""
UI Mappings for QuantStudio

This module contains mapping tables that convert between numeric menu selections
and their corresponding semantic values used in the system.
"""

# Language mapping: numeric selection -> actual language code
LANGUAGE_MAP = {
    1: "english",
    2: "french",
    3: "german",
    4: "spanish",
    5: "italian",
    6: "chinese",
    7: "hebrew",
    8: "arabic",
    9: "russian"
}

# Region mapping: numeric selection -> actual region code
REGION_MAP = {
    1: "America",
    2: "Europe",
    3: "Asia",
    4: "Middle-East"
}

# Universe mapping: numeric selection -> universe name
UNIVERSE_MAP = {
    1: "tech",
    2: "finance",
    3: "energy",
    4: "healthcare"
}

# Event type mapping: numeric selection -> event type
EVENT_TYPE_MAP = {
    1: "earnings",
    2: "breakout_20d_high",
    3: "volatility_compression",
    4: "volume_spike",
    5: "dividend_announcement",
    6: "round_number_reaction"
}

# Default values
DEFAULT_LANGUAGE = 1  # english
DEFAULT_REGION = 1    # America
DEFAULT_UNIVERSE = 1  # tech
DEFAULT_EVENT_TYPE = 1  # earnings
