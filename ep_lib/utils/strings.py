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