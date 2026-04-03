"""
Tests for EncryptionService.

Tests cover:
- AES-256-CBC encryption and decryption
- PBKDF2 key derivation
- IV and salt randomization
- Round-trip encryption/decryption
- Different passwords produce different ciphertexts
- Batch operations
- Error handling and edge cases
"""

import pytest
import json
from services.encryption_service import EncryptionService
from admin.constants import ENCRYPTION_SALT_LENGTH, ENCRYPTION_IV_LENGTH


@pytest.fixture
def encryption_service():
    """Create EncryptionService instance."""
    return EncryptionService("master_password_123")


@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return {
        "id": "q001",
        "image": "steve_jobs",
        "answer": "Steve Jobs",
        "answer_hash": "7d1a8f9b2c4e...",
        "answer_salt": "a7f2d9e1b5c3...",
        "category": "personalities",
        "difficulty": "easy",
        "hints": ["Steve", "Jobs", "Apple", "Founder"],
        "description": "Zakladatel Apple Inc.",
    }


class TestKeyDerivation:
    """Test PBKDF2 key derivation."""

    def test_derive_key_creates_key(self):
        """Key derivation should create a 256-bit key."""
        key, salt = EncryptionService.derive_key("password123")

        assert isinstance(key, bytes)
        assert isinstance(salt, bytes)
        assert len(key) == 32  # 256 bits = 32 bytes
        assert len(salt) == ENCRYPTION_SALT_LENGTH

    def test_derive_key_with_provided_salt(self):
        """Should use provided salt."""
        test_salt = b"a" * ENCRYPTION_SALT_LENGTH
        key, returned_salt = EncryptionService.derive_key("password123", test_salt)

        assert returned_salt == test_salt
        assert len(key) == 32

    def test_same_password_same_salt_produces_same_key(self):
        """Same password + salt should produce same key."""
        password = "password123"
        salt = b"b" * ENCRYPTION_SALT_LENGTH

        key1, _ = EncryptionService.derive_key(password, salt)
        key2, _ = EncryptionService.derive_key(password, salt)

        assert key1 == key2

    def test_different_salts_produce_different_keys(self):
        """Same password with different salts should produce different keys."""
        password = "password123"

        key1, _ = EncryptionService.derive_key(password, b"a" * ENCRYPTION_SALT_LENGTH)
        key2, _ = EncryptionService.derive_key(password, b"b" * ENCRYPTION_SALT_LENGTH)

        assert key1 != key2

    def test_different_passwords_produce_different_keys(self):
        """Different passwords should produce different keys."""
        salt = b"c" * ENCRYPTION_SALT_LENGTH

        key1, _ = EncryptionService.derive_key("password123", salt)
        key2, _ = EncryptionService.derive_key("password456", salt)

        assert key1 != key2


class TestIVGeneration:
    """Test random IV generation."""

    def test_generate_iv_correct_length(self):
        """Generated IV should be 16 bytes (128 bits)."""
        iv = EncryptionService.generate_iv()

        assert isinstance(iv, bytes)
        assert len(iv) == ENCRYPTION_IV_LENGTH

    def test_generate_iv_is_random(self):
        """Each generated IV should be different."""
        iv1 = EncryptionService.generate_iv()
        iv2 = EncryptionService.generate_iv()
        iv3 = EncryptionService.generate_iv()

        assert iv1 != iv2
        assert iv2 != iv3
        assert iv1 != iv3


class TestEncryption:
    """Test question encryption."""

    def test_encrypt_question_returns_dict(self, encryption_service, sample_question):
        """Encryption should return dictionary with required fields."""
        encrypted = encryption_service.encrypt_question(sample_question)

        assert isinstance(encrypted, dict)
        assert "encrypted_data" in encrypted
        assert "iv" in encrypted
        assert "salt" in encrypted
        assert "algorithm" in encrypted

    def test_encrypted_data_is_base64(self, encryption_service, sample_question):
        """Encrypted data should be base64 encoded."""
        encrypted = encryption_service.encrypt_question(sample_question)

        # Base64 strings contain only alphanumeric, +, /, =
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" 
                   for c in encrypted["encrypted_data"])
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" 
                   for c in encrypted["iv"])
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" 
                   for c in encrypted["salt"])

    def test_answer_is_not_in_encrypted_output(self, encryption_service, sample_question):
        """Answer should not appear in plaintext in encrypted output."""
        encrypted = encryption_service.encrypt_question(sample_question)

        # Check that answer is not in any of the base64 strings
        assert "Steve Jobs" not in encrypted["encrypted_data"]
        assert "Steve Jobs" not in encrypted["iv"]
        assert "Steve Jobs" not in encrypted["salt"]

    def test_encrypt_different_instances_different_iv(self, encryption_service, sample_question):
        """Each encryption should use different IV."""
        enc1 = encryption_service.encrypt_question(sample_question)
        enc2 = encryption_service.encrypt_question(sample_question)

        # Same question but different IVs
        assert enc1["encrypted_data"] != enc2["encrypted_data"]  # Different IV = different ciphertext
        assert enc1["iv"] != enc2["iv"]

    def test_encrypt_custom_password(self, sample_question):
        """Should be able to encrypt with custom password."""
        service = EncryptionService("default_password")
        encrypted = service.encrypt_question(sample_question, "custom_password123")

        assert "encrypted_data" in encrypted
        assert "salt" in encrypted
        assert "iv" in encrypted

    def test_encrypt_invalid_question_type(self, encryption_service):
        """Should raise error for non-dict question."""
        with pytest.raises(ValueError):
            encryption_service.encrypt_question("not a dict")

    def test_encrypt_large_question(self, encryption_service):
        """Should handle large question objects."""
        large_question = {
            "id": "q_large",
            "answer": "x" * 1000,
            "description": "y" * 5000,
            "hints": ["hint"] * 100,
        }
        encrypted = encryption_service.encrypt_question(large_question)

        assert "encrypted_data" in encrypted


class TestDecryption:
    """Test question decryption."""

    def test_decrypt_question_returns_dict(self, encryption_service, sample_question):
        """Decryption should return original dictionary."""
        encrypted = encryption_service.encrypt_question(sample_question)
        decrypted = encryption_service.decrypt_question(encrypted)

        assert isinstance(decrypted, dict)

    def test_decrypt_returns_original_question(self, encryption_service, sample_question):
        """Decrypted question should match original."""
        encrypted = encryption_service.encrypt_question(sample_question)
        decrypted = encryption_service.decrypt_question(encrypted)

        assert decrypted == sample_question

    def test_decrypt_preserves_nested_structures(self, encryption_service):
        """Should preserve nested dicts and lists."""
        question = {
            "id": "q001",
            "answer": "Test Answer",
            "metadata": {
                "created": "2026-04-02",
                "tags": ["tag1", "tag2"],
                "nested": {"deep": {"value": 42}},
            },
        }
        encrypted = encryption_service.encrypt_question(question)
        decrypted = encryption_service.decrypt_question(encrypted)

        assert decrypted == question
        assert decrypted["metadata"]["nested"]["deep"]["value"] == 42

    def test_decrypt_preserves_unicode(self, encryption_service):
        """Should preserve Unicode characters."""
        question = {
            "id": "q001",
            "answer": "Štěpán Žáka",
            "description": "Český язык السعربية 日本語",
        }
        encrypted = encryption_service.encrypt_question(question)
        decrypted = encryption_service.decrypt_question(encrypted)

        assert decrypted == question
        assert decrypted["answer"] == "Štěpán Žáka"

    def test_decrypt_missing_field_raises_error(self, encryption_service, sample_question):
        """Should raise error if encrypted dict missing required field."""
        encrypted = encryption_service.encrypt_question(sample_question)
        del encrypted["iv"]  # Remove IV

        with pytest.raises(ValueError):
            encryption_service.decrypt_question(encrypted)

    def test_decrypt_wrong_password_raises_error(self, encryption_service, sample_question):
        """Should raise error when trying to decrypt with wrong password."""
        encrypted = encryption_service.encrypt_question(sample_question)

        with pytest.raises(ValueError, match="wrong password"):
            encryption_service.decrypt_question(encrypted, "wrong_password")

    def test_decrypt_tampered_data_raises_error(self, encryption_service, sample_question):
        """Should raise error if encrypted data is tampered with."""
        encrypted = encryption_service.encrypt_question(sample_question)
        
        # Tamper with encrypted data (flip first character)
        tampered_char = chr((ord(encrypted["encrypted_data"][0]) + 1) % 256)
        encrypted["encrypted_data"] = tampered_char + encrypted["encrypted_data"][1:]

        with pytest.raises(ValueError):
            encryption_service.decrypt_question(encrypted)

    def test_decrypt_custom_password(self, sample_question):
        """Should be able to decrypt with correct custom password."""
        service = EncryptionService("default_password")
        custom_password = "my_custom_password_456"

        encrypted = service.encrypt_question(sample_question, custom_password)
        decrypted = service.decrypt_question(encrypted, custom_password)

        assert decrypted == sample_question

    def test_decrypt_fails_with_wrong_custom_password(self, sample_question):
        """Should fail to decrypt with wrong custom password."""
        service = EncryptionService("default_password")

        encrypted = service.encrypt_question(sample_question, "correct_password")

        with pytest.raises(ValueError):
            service.decrypt_question(encrypted, "wrong_password")


class TestRoundTrip:
    """Test full encryption/decryption round trips."""

    def test_round_trip_simple(self, encryption_service):
        """Simple question should survive round trip."""
        original = {
            "id": "q001",
            "answer": "Answer Text",
        }
        encrypted = encryption_service.encrypt_question(original)
        decrypted = encryption_service.decrypt_question(encrypted)

        assert decrypted == original

    def test_round_trip_complex(self, encryption_service, sample_question):
        """Complex question should survive round trip."""
        encrypted = encryption_service.encrypt_question(sample_question)
        decrypted = encryption_service.decrypt_question(encrypted)

        assert decrypted == sample_question

    def test_round_trip_multiple_times(self, encryption_service, sample_question):
        """Question should survive multiple round trips."""
        question = sample_question.copy()

        for i in range(5):
            encrypted = encryption_service.encrypt_question(question)
            question = encryption_service.decrypt_question(encrypted)

        assert question == sample_question

    def test_round_trip_with_different_passwords(self, sample_question):
        """Should handle different passwords correctly."""
        service = EncryptionService("default")

        # Encrypt with password1
        password1 = "password_one_123"
        encrypted = service.encrypt_question(sample_question, password1)

        # Decrypt with password1 should work
        decrypted = service.decrypt_question(encrypted, password1)
        assert decrypted == sample_question

        # Decrypt with password2 should fail
        with pytest.raises(ValueError):
            service.decrypt_question(encrypted, "password_two_456")


class TestBatchOperations:
    """Test batch encryption/decryption."""

    def test_encrypt_batch(self, encryption_service):
        """Should encrypt multiple questions."""
        questions = [
            {"id": "q001", "answer": "Answer 1"},
            {"id": "q002", "answer": "Answer 2"},
            {"id": "q003", "answer": "Answer 3"},
        ]

        encrypted_list = encryption_service.encrypt_questions_batch(questions)

        assert len(encrypted_list) == 3
        for encrypted in encrypted_list:
            assert "encrypted_data" in encrypted

    def test_decrypt_batch(self, encryption_service):
        """Should decrypt multiple questions."""
        questions = [
            {"id": "q001", "answer": "Answer 1"},
            {"id": "q002", "answer": "Answer 2"},
            {"id": "q003", "answer": "Answer 3"},
        ]

        encrypted_list = encryption_service.encrypt_questions_batch(questions)
        decrypted_list = encryption_service.decrypt_questions_batch(encrypted_list)

        assert decrypted_list == questions

    def test_batch_each_unique_iv(self, encryption_service):
        """Each question in batch should have unique IV."""
        questions = [{"id": "q001", "answer": "Answer 1"}] * 3

        encrypted_list = encryption_service.encrypt_questions_batch(questions)

        ivs = [e["iv"] for e in encrypted_list]
        assert len(set(ivs)) == 3  # All unique


class TestSecurityProperties:
    """Test security properties."""

    def test_answer_never_in_plaintext_output(self, encryption_service):
        """Answer should never appear in plaintext anywhere."""
        question = {
            "id": "q001",
            "answer": "SuperSecretAnswer123",
            "hints": ["hint"],
        }

        encrypted = encryption_service.encrypt_question(question)
        encrypted_json = json.dumps(encrypted)

        assert "SuperSecretAnswer123" not in encrypted_json

    def test_different_encryptions_of_same_question_different(self, encryption_service):
        """Same question encrypted twice should produce different results."""
        question = {"id": "q001", "answer": "Answer"}

        enc1 = encryption_service.encrypt_question(question)
        enc2 = encryption_service.encrypt_question(question)

        # Different IVs lead to different ciphertexts
        assert enc1["encrypted_data"] != enc2["encrypted_data"]
        assert enc1["iv"] != enc2["iv"]

    def test_iv_uniqueness_across_many_encryptions(self, encryption_service):
        """IVs should be unique across many encryptions."""
        question = {"id": "q001", "answer": "Answer"}

        ivs = []
        for _ in range(100):
            encrypted = encryption_service.encrypt_question(question)
            ivs.append(encrypted["iv"])

        # All IVs should be unique
        assert len(set(ivs)) == 100


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self):
        """Test complete encryption workflow."""
        # Setup
        service = EncryptionService("master_admin_password")

        # Create question
        question = {
            "id": "q_integration_001",
            "image": "test_image",
            "answer": "This is the secret answer",
            "hints": ["secret", "answer"],
            "category": "test",
        }

        # Encrypt
        encrypted = service.encrypt_question(question)

        # Simulate storage (convert to JSON)
        stored = json.dumps(encrypted)

        # Simulate loading (convert from JSON)
        loaded = json.loads(stored)

        # Decrypt
        decrypted = service.decrypt_question(loaded)

        # Verify
        assert decrypted == question
        assert "secret answer" not in stored  # Answer not in stored JSON

    def test_multiple_admins_same_password(self):
        """Multiple admin instances with same password should decrypt same data."""
        password = "shared_admin_password"

        admin1 = EncryptionService(password)
        admin2 = EncryptionService(password)

        question = {"id": "q001", "answer": "Answer"}

        encrypted = admin1.encrypt_question(question, password)
        decrypted = admin2.decrypt_question(encrypted, password)

        assert decrypted == question

    def test_multiple_admins_different_passwords_isolation(self):
        """Different passwords should provide data isolation."""
        question1 = {"id": "q001", "answer": "Secret Answer 1"}
        question2 = {"id": "q002", "answer": "Secret Answer 2"}

        admin1 = EncryptionService("admin1_password")
        admin2 = EncryptionService("admin2_password")

        # Encrypt with different passwords
        enc1 = admin1.encrypt_question(question1, "admin1_password")
        enc2 = admin2.encrypt_question(question2, "admin2_password")

        # Cross-decryption should fail
        with pytest.raises(ValueError):
            admin1.decrypt_question(enc2, "admin1_password")

        with pytest.raises(ValueError):
            admin2.decrypt_question(enc1, "admin2_password")

        # Same admin with correct password should work
        assert admin1.decrypt_question(enc1, "admin1_password") == question1
        assert admin2.decrypt_question(enc2, "admin2_password") == question2
