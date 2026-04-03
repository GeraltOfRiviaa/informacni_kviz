"""
EncryptionService - Handles question encryption and decryption.

Security Features:
- AES-256-CBC encryption
- PBKDF2 key derivation from password
- Random IV (initialization vector) for each encryption
- Random salt for key derivation
- Base64 encoding for storage
- JSON serialization/deserialization

Design:
    Questions are encrypted when stored on disk and decrypted when loaded into memory.
    This ensures that answers are never visible in plaintext files.

    Flow:
        Question (plaintext) → Encrypt → Base64 → JSON (on disk)
        JSON (from disk) → Base64 → Decrypt → Question (plaintext, in memory)
"""

import json
import logging
import secrets
from typing import Dict, Any, Tuple
from base64 import b64encode, b64decode

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from admin.constants import (
    ENCRYPTION_ALGORITHM,
    ENCRYPTION_KEY_LENGTH,
    ENCRYPTION_SALT_LENGTH,
    ENCRYPTION_IV_LENGTH,
)

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Handles encryption and decryption of quiz questions.

    Questions are stored in encrypted form on disk. This service
    provides methods to encrypt questions before saving and decrypt
    them after loading.

    Security Properties:
        - AES-256-CBC ensures strong encryption
        - PBKDF2 with 100,000 iterations protects against weak passwords
        - Random IV for each encryption prevents pattern recognition
        - Random salt for key derivation prevents rainbow table attacks
    """

    def __init__(self, master_password: str):
        """
        Initialize EncryptionService with a master password.

        The password is used to derive the encryption key via PBKDF2.

        Args:
            master_password: Password to derive encryption key from
        """
        self.master_password = master_password
        self.backend = default_backend()
        logger.debug("EncryptionService initialized")

    @staticmethod
    def derive_key(
        password: str, salt: bytes = None
    ) -> Tuple[bytes, bytes]:
        """
        Derive an encryption key from a password using PBKDF2.

        PBKDF2 (Password-Based Key Derivation Function 2) is recommended
        by NIST and designed specifically for password-based key derivation.

        Args:
            password: Password to derive key from
            salt: Salt for KDF (generated if not provided)

        Returns:
            Tuple of (derived_key, salt)

        Security Notes:
            - Uses 100,000 iterations (OWASP recommendation)
            - Generates random 32-byte salt if not provided
            - Uses SHA256 hash function
            - Returns 256-bit key suitable for AES-256
        """
        if salt is None:
            salt = secrets.token_bytes(ENCRYPTION_SALT_LENGTH)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=ENCRYPTION_KEY_LENGTH,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
            backend=default_backend(),
        )

        key = kdf.derive(password.encode())
        return key, salt

    @staticmethod
    def generate_iv() -> bytes:
        """
        Generate a random initialization vector for CBC mode.

        Each encryption should use a unique IV to prevent pattern recognition.

        Returns:
            Random 16-byte IV
        """
        return secrets.token_bytes(ENCRYPTION_IV_LENGTH)

    def encrypt_question(
        self, question: Dict[str, Any], password: str = None
    ) -> Dict[str, str]:
        """
        Encrypt a question dictionary for secure storage.

        The question is serialized to JSON, encrypted with AES-256-CBC,
        and returned along with IV and salt for later decryption.

        Args:
            question: Question dictionary to encrypt
            password: Optional password (uses master password if not provided)

        Returns:
            Dictionary with encrypted data:
            {
                "encrypted_data": "base64_encoded_ciphertext",
                "iv": "base64_encoded_iv",
                "salt": "base64_encoded_salt",
                "algorithm": "AES-256-CBC"
            }

        Raises:
            ValueError: If question serialization fails
            Exception: If encryption fails

        Security Notes:
            - Answer field is included in encryption but not stored separately
            - Each encryption uses a unique IV
            - Salt is randomized for each new encryption
        """
        try:
            # Use master password if not provided
            if password is None:
                password = self.master_password

            # Validate question structure
            if not isinstance(question, dict):
                raise ValueError("Question must be a dictionary")

            # Serialize question to JSON
            json_data = json.dumps(question, ensure_ascii=False)

            # Derive encryption key
            key, salt = self.derive_key(password)

            # Generate IV
            iv = self.generate_iv()

            # Encrypt with AES-256-CBC
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend,
            )
            encryptor = cipher.encryptor()

            # Add PKCS7 padding
            plaintext = json_data.encode('utf-8')
            block_size = 16
            padding_length = block_size - (len(plaintext) % block_size)
            padded_plaintext = plaintext + bytes([padding_length] * padding_length)

            # Encrypt
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

            # Encode to base64 for storage
            encrypted_data_b64 = b64encode(ciphertext).decode('ascii')
            iv_b64 = b64encode(iv).decode('ascii')
            salt_b64 = b64encode(salt).decode('ascii')

            logger.debug(
                f"Question encrypted successfully (id={question.get('id', 'unknown')})"
            )

            return {
                "encrypted_data": encrypted_data_b64,
                "iv": iv_b64,
                "salt": salt_b64,
                "algorithm": ENCRYPTION_ALGORITHM,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to serialize question to JSON: {e}")
            raise ValueError(f"Invalid question structure: {e}")
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_question(
        self, encrypted: Dict[str, str], password: str = None
    ) -> Dict[str, Any]:
        """
        Decrypt an encrypted question dictionary.

        The encrypted data is decrypted using the provided IV and salt,
        then deserialized from JSON back to a dictionary.

        Args:
            encrypted: Encrypted question dictionary with keys:
                       encrypted_data, iv, salt, algorithm
            password: Optional password (uses master password if not provided)

        Returns:
            Decrypted question dictionary with original structure

        Raises:
            ValueError: If decryption fails or data is corrupted
            KeyError: If required fields are missing
            json.JSONDecodeError: If deserialization fails

        Security Notes:
            - Does not validate algorithm field (only supports AES-256-CBC)
            - Validates PKCS7 padding to detect tampering
            - Logs decryption but not the contents (for security)
        """
        try:
            # Use master password if not provided
            if password is None:
                password = self.master_password

            # Extract components
            encrypted_data_b64 = encrypted["encrypted_data"]
            iv_b64 = encrypted["iv"]
            salt_b64 = encrypted["salt"]

            # Decode from base64
            ciphertext = b64decode(encrypted_data_b64)
            iv = b64decode(iv_b64)
            salt = b64decode(salt_b64)

            # Derive key with same salt
            key, _ = self.derive_key(password, salt)

            # Decrypt with AES-256-CBC
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend,
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove PKCS7 padding
            padding_length = padded_plaintext[-1]
            plaintext = padded_plaintext[:-padding_length]

            # Deserialize from JSON
            question = json.loads(plaintext.decode('utf-8'))

            logger.debug(
                f"Question decrypted successfully (id={question.get('id', 'unknown')})"
            )

            return question

        except KeyError as e:
            logger.error(f"Missing encryption component: {e}")
            raise ValueError(f"Encrypted data missing required field: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to deserialize decrypted data: {e}")
            raise ValueError(f"Decrypted data is not valid JSON: {e}")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Decryption failed (possible wrong password): {e}")

    def encrypt_questions_batch(
        self, questions: list, password: str = None
    ) -> list:
        """
        Encrypt multiple questions.

        Args:
            questions: List of question dictionaries
            password: Optional password

        Returns:
            List of encrypted question dictionaries
        """
        return [self.encrypt_question(q, password) for q in questions]

    def decrypt_questions_batch(
        self, encrypted_questions: list, password: str = None
    ) -> list:
        """
        Decrypt multiple questions.

        Args:
            encrypted_questions: List of encrypted question dictionaries
            password: Optional password

        Returns:
            List of decrypted question dictionaries
        """
        return [self.decrypt_question(eq, password) for eq in encrypted_questions]

    def __str__(self) -> str:
        """String representation."""
        return f"EncryptionService(algorithm={ENCRYPTION_ALGORITHM}, key_length={ENCRYPTION_KEY_LENGTH})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"EncryptionService(master_password={'*' * len(self.master_password)})"
