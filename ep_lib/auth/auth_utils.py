import re
import json
import time
from typing import Tuple

from flask import current_app as app
from cryptography.fernet import Fernet


def encrypt_change_password_token(email):
    SECRET_KEY = app.config["SECRET_KEY"]
    timestamp = str(int(time.time()))
    data_to_encrypt = {"email": email, "timestamp": timestamp}
    data_json = json.dumps(data_to_encrypt).encode()
    cipher_suite = Fernet(SECRET_KEY)
    encrypted_token = cipher_suite.encrypt(data_json)
    return encrypted_token.decode()


def decrypt_token(token):
    SECRET_KEY = app.config["SECRET_KEY"]
    cipher_suite = Fernet(SECRET_KEY)
    decrypted_token = cipher_suite.decrypt(token.encode())
    decrypted_data_json = decrypted_token.decode()
    decrypted_data = json.loads(decrypted_data_json)
    return decrypted_data



def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, ""


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))