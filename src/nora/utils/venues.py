import re
from typing import Union, Dict, Optional
from omegaconf import OmegaConf
from rapidfuzz import process, fuzz


def parse_venue(
    text: str,
    venues_dict: Union[OmegaConf, Dict],
    fuzzy_threshold: int = 85
) -> Optional[str]:
    """Given a venue string, try to find if an acronym is available in
    the config file.

    Priority:
        1. Exact matches of full-text keys (longer first)
        2. Exact matches of acronyms (longer first)
        3. Fuzzy fallback if nothing matches
    """
    if text is None:
        return None

    if isinstance(venues_dict, OmegaConf):
        venues_dict = OmegaConf.to_container(venues_dict, resolve=True)

    # Normalize input text
    text_norm = text.lower()

    # Sort keys by length (descending)
    sorted_keys = sorted(venues_dict.keys(), key=len, reverse=True)
    sorted_acronyms = sorted(set(venues_dict.values()), key=len, reverse=True)
    sorted_keys = sorted_keys + sorted_acronyms

    # Exact (regex) matching
    for key in sorted_keys:
        key_norm = key.lower()
        pattern = r'\b' + re.escape(key_norm) + r'\b'
        if re.search(pattern, text_norm):
            if key in venues_dict:
                return venues_dict[key]
            return key

    # Fuzzy matching fallback
    candidates = list(venues_dict.keys()) + list(venues_dict.values())
    best, score, _ = process.extractOne(
        text_norm,
        candidates,
        scorer=fuzz.partial_ratio)
    if best is not None and score >= fuzzy_threshold:
        if best in venues_dict:
            return venues_dict[best]
        else:
            return best  # It was an acronym

    # No match found
    return None
