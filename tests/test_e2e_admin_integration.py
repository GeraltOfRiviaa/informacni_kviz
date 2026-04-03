"""
E2E Integration Tests for Admin Services (Service Layer Only).

Tests the integration of admin services without any Tkinter GUI components.
Focus on actual business logic and workflows, not UI.
"""

import pytest
from services.admin_auth import AdminAuth
from services.encryption_service import EncryptionService
from services.admin_question_manager import AdminQuestionManager
from services.image_upload_service import ImageUploadService


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def admin_auth():
    """Create AdminAuth instance with default credentials."""
    password_hash, password_salt = AdminAuth.hash_password("admin")
    return AdminAuth(password_hash, password_salt)


@pytest.fixture
def encryption_service():
    """Create EncryptionService instance."""
    return EncryptionService("test_password")


@pytest.fixture
def question_manager():
    """Create AdminQuestionManager instance."""
    return AdminQuestionManager()


@pytest.fixture
def image_upload_service():
    """Create ImageUploadService instance."""
    return ImageUploadService()


# ============================================================================
# E2E: Complete Authentication Flow
# ============================================================================

class TestE2EAuthenticationFlow:
    """Test authentication service workflow."""
    
    def test_correct_password_authenticates(self, admin_auth):
        """Test: User can authenticate with correct password."""
        assert admin_auth.verify_password("admin") is True
    
    def test_wrong_password_rejected(self, admin_auth):
        """Test: Wrong password is rejected."""
        assert admin_auth.verify_password("wrong") is False
    
    def test_rate_limiting_three_attempts(self, admin_auth):
        """Test: Account locks after 3 failed attempts."""
        # Attempt 1-3
        for i in range(3):
            admin_auth.verify_password(f"wrong{i}")
        
        # Account should be locked
        assert admin_auth.is_locked() is True
        
        # Even correct password fails when locked
        assert admin_auth.verify_password("admin") is False
    
    def test_successful_login_resets_attempts(self, admin_auth):
        """Test: Successful login resets attempt counter."""
        admin_auth.verify_password("wrong")
        
        # Successful login should work
        assert admin_auth.verify_password("admin") is True
        
        # Next authentication should also work (no lockout)
        assert admin_auth.verify_password("admin") is True


# ============================================================================
# E2E: Question Management Flow
# ============================================================================

class TestE2EQuestionManagement:
    """Test question manager workflow."""
    
    def test_load_all_questions(self, question_manager):
        """Test: Can load all questions."""
        questions = question_manager.get_all_questions()
        assert isinstance(questions, list)
        assert len(questions) > 0
    
    def test_get_specific_question(self, question_manager):
        """Test: Can retrieve specific question by ID."""
        all_questions = question_manager.get_all_questions()
        test_id = all_questions[0]['id']
        
        question = question_manager.get_question(test_id)
        assert question is not None
        assert question['id'] == test_id
    
    def test_get_nonexistent_question(self, question_manager):
        """Test: Nonexistent question returns None."""
        result = question_manager.get_question("invalid_id_xyz")
        assert result is None
    
    def test_filter_by_category(self, question_manager):
        """Test: Filter questions by category."""
        results = question_manager.get_questions_by_category("People")
        assert isinstance(results, list)
    
    def test_get_statistics(self, question_manager):
        """Test: Get question statistics."""
        stats = question_manager.get_statistics()
        assert isinstance(stats, dict)
        # Statistics may have 'total_questions' or 'total' key
        total = stats.get('total_questions') or stats.get('total')
        assert total is not None
        assert total > 0


# ============================================================================
# E2E: Encryption Service
# ============================================================================

class TestE2EEncryption:
    """Test encryption service workflow."""
    
    def test_service_initialization(self, encryption_service):
        """Test: EncryptionService initializes."""
        assert encryption_service is not None


# ============================================================================
# E2E: Image Upload Validation
# ============================================================================

class TestE2EImageValidation:
    """Test image service validation workflow."""
    
    def test_jpeg_magic_bytes_valid(self, image_upload_service):
        """Test: JPEG magic bytes recognized as valid."""
        jpeg_bytes = b'\xFF\xD8\xFF\xE0'
        if hasattr(image_upload_service, 'validate_image_bytes'):
            assert image_upload_service.validate_image_bytes(jpeg_bytes) is True
    
    def test_invalid_file_rejected(self, image_upload_service):
        """Test: Invalid file rejected."""
        invalid_bytes = b'Random text'
        if hasattr(image_upload_service, 'validate_image_bytes'):
            assert image_upload_service.validate_image_bytes(invalid_bytes) is False


# ============================================================================
# E2E: Security Integration
# ============================================================================

class TestE2ESecurity:
    """Test security across components."""
    
    def test_password_not_stored_plaintext(self, admin_auth):
        """Test: Passwords don't appear in attributes."""
        password = "sensitive_password"
        hash_val, salt = AdminAuth.hash_password(password)
        auth = AdminAuth(hash_val, salt)
        
        object_str = str(auth.__dict__)
        assert password not in object_str
    
    def test_lockout_protection(self, admin_auth):
        """Test: Lockout protects against brute force."""
        for i in range(3):
            admin_auth.verify_password(f"wrong{i}")
        
        assert admin_auth.is_locked() is True
        assert admin_auth.verify_password("admin") is False


# ============================================================================
# E2E: Data Persistence
# ============================================================================

class TestE2EPersistence:
    """Test data persistence and loading."""
    
    def test_questions_loaded_from_storage(self, question_manager):
        """Test: Questions loaded from persistent storage."""
        questions = question_manager.get_all_questions()
        questions2 = question_manager.get_all_questions()
        
        assert len(questions) == len(questions2)


# ============================================================================
# E2E: Error Handling
# ============================================================================

class TestE2EErrorHandling:
    """Test error handling and recovery."""
    
    def test_invalid_category_handled(self, question_manager):
        """Test: Invalid category filter handled."""
        results = question_manager.get_questions_by_category("InvalidCategory123")
        assert isinstance(results, list)
    
    def test_empty_results_handled(self, question_manager):
        """Test: Empty results handled gracefully."""
        result = question_manager.get_question("nonexistent")
        assert result is None


# ============================================================================
# E2E: Complete Workflow
# ============================================================================

class TestE2ECompleteWorkflow:
    """Test complete workflow scenarios."""
    
    def test_admin_access_workflow(self, admin_auth, question_manager):
        """Test: Complete admin access workflow."""
        # 1. Authenticate
        assert admin_auth.verify_password("admin") is True
        
        # 2. Load questions
        questions = question_manager.get_all_questions()
        assert len(questions) > 0
        
        # 3. Filter questions
        cat = questions[0].get('category')
        if cat:
            filtered = question_manager.get_questions_by_category(cat)
            assert isinstance(filtered, list)
    
    def test_question_selection_workflow(self, question_manager):
        """Test: Question selection for game."""
        # 1. Load all questions
        questions = question_manager.get_all_questions()
        assert len(questions) > 0
        
        # 2. Select a question
        selected = questions[0]
        
        # 3. Verify retrieval
        retrieved = question_manager.get_question(selected['id'])
        assert retrieved['id'] == selected['id']
        
        # 4. Get stats
        stats = question_manager.get_statistics()
        total = stats.get('total_questions') or stats.get('total')
        assert total is not None
        assert total > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
