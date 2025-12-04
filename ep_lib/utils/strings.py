import math
import re
from typing import List
import unicodedata
import uuid
import pandas as pd


def generate_id():
    return uuid.uuid4().hex.upper()


def clean_value(value):
    """Convert pandas NaN to None, handle empty strings and other null-like values"""
    if pd.isna(value):
        return None
    if value == '' or value == 'None' or value == 'null':
        return None
    return value

def safe_str(value, default=""):
    """Safely convert any value to a normalized lowercase string.
    Handles None, NaN, strips whitespace, and removes accents (é -> e, ç -> c, etc.)."""
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default

    # Convert to string and strip
    text = str(value).strip().lower()

    # Normalize accents: é -> e, ç -> c, etc.
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")

    # Collapse repeating whitespace to a single space
    text = re.sub(r"\s+", " ", text)

    return text

def clean_text(value) -> str:
    """
    Normalize text by converting None to an empty string and stripping whitespace.

    Args:
        value: Any input value.

    Returns:
        str: A trimmed string, or "" if the value is None.
    """
    if value is None:
        return ""
    return str(value).strip()
        
def is_valid_string(series):
    """
    Return a boolean Series indicating which values are valid non-empty strings.

    A value is considered valid if:
    - It is not NaN
    - It is an instance of `str`
    - It is not empty after trimming whitespace

    Args:
        series (pd.Series): The input pandas Series.

    Returns:
        pd.Series: Boolean mask where True means the value is a valid string.
    """
    return series.apply(lambda x: isinstance(x, str) and x.strip() != '' if pd.notna(x) else False)


def to_token_list(*values) -> List[str]:
    """
    Convert one or more values into a flat list of unique, normalized tokens.

    - Accepts strings, lists, tuples, or sets.
    - Splits strings using common separators: ',', ';', '|', '/'.
    - Normalizes each item using safe_str().
    - Removes duplicates while preserving the original order.

    Returns:
        List[str]: A list of unique tokens.
    """
    tokens: List[str] = []
    separators = [",", ";", "|", "/"]

    for raw in values:
        if not raw:
            continue

        if isinstance(raw, (list, tuple, set)):
            iterable = raw
        else:
            text = str(raw)
            split_values = [text]
            for sep in separators:
                if sep in text:
                    split_values = [part.strip() for part in text.split(sep)]
                    break
            iterable = split_values

        for item in iterable:
            token = safe_str(item)
            if token and token not in tokens:
                tokens.append(token)

    return tokens