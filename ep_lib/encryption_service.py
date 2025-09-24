from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Optional


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data using Fernet symmetric encryption.
    Uses the application's SECRET_KEY as the base for key derivation.
    """
    
    def __init__(self, secret_key: str):
        """
        Initialize the encryption service with a secret key.
        
        Args:
            secret_key (str): The secret key used for key derivation
        """
        self.secret_key = secret_key.encode()
        self._fernet = None
    
    def _get_fernet(self) -> Fernet:
        """
        Get or create a Fernet instance with a key derived from the secret key.
        
        Returns:
            Fernet: The encryption/decryption instance
        """
        if self._fernet is None:
            # Use a fixed salt for consistent key derivation
            # In production, you might want to store this salt securely
            salt = b'smit_mail_config_salt_2024'
            
            # Derive a key from the secret key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key))
            self._fernet = Fernet(key)
        
        return self._fernet
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext (str): The string to encrypt
            
        Returns:
            str: The encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""
        
        try:
            fernet = self._get_fernet()
            encrypted_bytes = fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted_text (str): The encrypted string (base64 encoded)
            
        Returns:
            str: The decrypted plaintext string
        """
        if not encrypted_text:
            return ""
        
        try:
            fernet = self._get_fernet()
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def is_encrypted(self, text: str) -> bool:
        """
        Check if a string appears to be encrypted (basic heuristic).
        
        Args:
            text (str): The string to check
            
        Returns:
            bool: True if the string appears to be encrypted
        """
        if not text:
            return False
        
        try:
            # Try to decode as base64 - encrypted strings should be base64 encoded
            base64.urlsafe_b64decode(text.encode())
            # If it's base64 and has a reasonable length, it might be encrypted
            return len(text) > 20 and len(text) % 4 == 0
        except Exception:
            return False


# Global instance - will be initialized with the actual SECRET_KEY
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service(secret_key: str) -> EncryptionService:
    """
    Get the global encryption service instance.
    
    Args:
        secret_key (str): The secret key for encryption
        
    Returns:
        EncryptionService: The encryption service instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService(secret_key)
    return _encryption_service


def encrypt_password(password: str, secret_key: str) -> str:
    """
    Convenience function to encrypt a password.
    
    Args:
        password (str): The password to encrypt
        secret_key (str): The secret key for encryption
        
    Returns:
        str: The encrypted password
    """
    service = get_encryption_service(secret_key)
    return service.encrypt(password)


def decrypt_password(encrypted_password: str, secret_key: str) -> str:
    """
    Convenience function to decrypt a password.
    
    Args:
        encrypted_password (str): The encrypted password
        secret_key (str): The secret key for decryption
        
    Returns:
        str: The decrypted password
    """
    service = get_encryption_service(secret_key)
    return service.decrypt(encrypted_password)


def is_password_encrypted(password: str) -> bool:
    """
    Check if a password appears to be encrypted.
    
    Args:
        password (str): The password to check
        
    Returns:
        bool: True if the password appears to be encrypted
    """
    if not password:
        return False
    
    try:
        # Try to decode as base64 - encrypted strings should be base64 encoded
        base64.urlsafe_b64decode(password.encode())
        # If it's base64 and has a reasonable length, it might be encrypted
        return len(password) > 20 and len(password) % 4 == 0
    except Exception:
        return False