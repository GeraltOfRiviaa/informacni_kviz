"""
Tests for AdminQuestionManager service.

Coverage:
- Question creation with validation
- Question retrieval (single, all, by category)
- Question updates (fields, answer changes)
- Question deletion
- Answer verification with normalization
- Question validation
- Statistics generation
- Import/export functionality
- Error handling and edge cases
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from services.admin_question_manager import AdminQuestionManager
from services.answer_checker import AnswerChecker


@pytest.fixture
def temp_questions_file():
    """Create a temporary questions file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"questions": []}, f)
        temp_path = f.name
    yield temp_path
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_questions_with_data():
    """Create a temporary questions file with initial data."""
    initial_data = {
        "questions": [
            {
                "id": "q001",
                "category": "personality",
                "image_id": "img_001",
                "answer_hash": "abc123",
                "answer_salt": "def456",
                "answer_length": 5,
                "difficulty": "easy",
                "description": "Test question 1",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            {
                "id": "q002",
                "category": "logo",
                "image_id": "img_002",
                "answer_hash": "xyz789",
                "answer_salt": "uvw012",
                "answer_length": 6,
                "difficulty": "medium",
                "description": "Test question 2",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(initial_data, f)
        temp_path = f.name
    yield temp_path
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def manager(temp_questions_file):
    """Create an AdminQuestionManager instance."""
    return AdminQuestionManager(questions_file=temp_questions_file)


@pytest.fixture
def manager_with_data(temp_questions_with_data):
    """Create an AdminQuestionManager with initial data."""
    return AdminQuestionManager(questions_file=temp_questions_with_data)


class TestQuestionCreation:
    """Test question creation."""

    def test_create_question_basic(self, manager):
        """Test creating a basic question."""
        q = manager.create_question(
            category="personality",
            image_id="img_steve",
            answer="Steve Jobs",
            difficulty="medium",
        )

        assert q["id"].startswith("q")
        assert q["category"] == "personality"
        assert q["image_id"] == "img_steve"
        assert q["difficulty"] == "medium"
        assert "answer_hash" in q
        assert "answer_salt" in q
        assert "created_at" in q

    def test_create_question_with_description(self, manager):
        """Test creating question with description."""
        q = manager.create_question(
            category="logo",
            image_id="img_google",
            answer="Google",
            difficulty="easy",
            description="Search engine logo",
        )

        assert q["description"] == "Search engine logo"

    def test_create_question_with_hints(self, manager):
        """Test creating question with hints."""
        hints = ["Computer company", "Founded by Steve Jobs"]
        q = manager.create_question(
            category="personality",
            image_id="img_001",
            answer="Apple",
            hints=hints,
        )

        assert q["hints"] == hints

    def test_create_multiple_questions_unique_ids(self, manager):
        """Test that multiple questions get unique IDs."""
        q1 = manager.create_question(
            category="logo", image_id="img_1", answer="Apple"
        )
        q2 = manager.create_question(
            category="logo", image_id="img_2", answer="Google"
        )
        q3 = manager.create_question(
            category="logo", image_id="img_3", answer="Microsoft"
        )

        assert q1["id"] != q2["id"] != q3["id"]
        assert q1["id"] == "q001"
        assert q2["id"] == "q002"
        assert q3["id"] == "q003"

    def test_create_question_missing_category(self, manager):
        """Test validation: missing category raises error."""
        with pytest.raises(ValueError):
            manager.create_question(
                category="",
                image_id="img_001",
                answer="Test",
            )

    def test_create_question_missing_image_id(self, manager):
        """Test validation: missing image_id raises error."""
        with pytest.raises(ValueError):
            manager.create_question(
                category="personality",
                image_id="",
                answer="Test",
            )

    def test_create_question_invalid_difficulty(self, manager):
        """Test validation: invalid difficulty raises error."""
        with pytest.raises(ValueError):
            manager.create_question(
                category="personality",
                image_id="img_001",
                answer="Test",
                difficulty="ultra_hard",
            )


class TestQuestionRetrieval:
    """Test question retrieval operations."""

    def test_get_question_by_id(self, manager_with_data):
        """Test retrieving a question by ID."""
        q = manager_with_data.get_question("q001")

        assert q is not None
        assert q["id"] == "q001"
        assert q["category"] == "personality"

    def test_get_nonexistent_question(self, manager_with_data):
        """Test getting non-existent question returns None."""
        q = manager_with_data.get_question("q999")
        assert q is None

    def test_get_all_questions(self, manager_with_data):
        """Test getting all questions."""
        questions = manager_with_data.get_all_questions()

        assert len(questions) == 2
        assert questions[0]["id"] == "q001"
        assert questions[1]["id"] == "q002"

    def test_get_all_questions_excludes_sensitive_data(self, manager_with_data):
        """Test that get_all_questions excludes answer hashes."""
        questions = manager_with_data.get_all_questions()

        for q in questions:
            assert "answer_hash" not in q
            assert "answer_salt" not in q

    def test_get_questions_by_category(self, manager_with_data):
        """Test filtering questions by category."""
        personality_q = manager_with_data.get_questions_by_category("personality")
        logo_q = manager_with_data.get_questions_by_category("logo")

        assert len(personality_q) == 1
        assert personality_q[0]["id"] == "q001"

        assert len(logo_q) == 1
        assert logo_q[0]["id"] == "q002"

    def test_get_questions_by_nonexistent_category(self, manager_with_data):
        """Test filtering by non-existent category returns empty."""
        questions = manager_with_data.get_questions_by_category("hardware")
        assert len(questions) == 0


class TestQuestionUpdate:
    """Test question update operations."""

    def test_update_question_difficulty(self, manager_with_data):
        """Test updating question difficulty."""
        updated = manager_with_data.update_question(
            "q001",
            {"difficulty": "hard"}
        )

        assert updated["difficulty"] == "hard"
        assert manager_with_data.get_question("q001")["difficulty"] == "hard"

    def test_update_question_description(self, manager_with_data):
        """Test updating question description."""
        updated = manager_with_data.update_question(
            "q001",
            {"description": "New description"}
        )

        assert updated["description"] == "New description"

    def test_update_question_answer(self, manager_with_data):
        """Test updating the answer (hashes it)."""
        updated = manager_with_data.update_question(
            "q001",
            {"answer": "New Answer"}
        )

        assert updated["answer_length"] == len("New Answer")
        assert "answer_hash" in updated
        assert "answer_salt" in updated

    def test_update_nonexistent_question_raises_error(self, manager_with_data):
        """Test updating non-existent question raises error."""
        with pytest.raises(ValueError):
            manager_with_data.update_question("q999", {"difficulty": "hard"})

    def test_update_sets_updated_at(self, manager_with_data):
        """Test that update sets updated_at timestamp."""
        original_updated = manager_with_data.get_question("q001")["updated_at"]

        manager_with_data.update_question("q001", {"difficulty": "hard"})
        new_updated = manager_with_data.get_question("q001")["updated_at"]

        assert new_updated >= original_updated


class TestQuestionDeletion:
    """Test question deletion operations."""

    def test_delete_existing_question(self, manager_with_data):
        """Test deleting an existing question."""
        result = manager_with_data.delete_question("q001")

        assert result is True
        assert manager_with_data.get_question("q001") is None
        assert len(manager_with_data.get_all_questions()) == 1

    def test_delete_nonexistent_question(self, manager_with_data):
        """Test deleting non-existent question returns False."""
        result = manager_with_data.delete_question("q999")
        assert result is False

    def test_delete_persists(self, temp_questions_with_data):
        """Test that deletion persists to file."""
        manager = AdminQuestionManager(questions_file=temp_questions_with_data)
        manager.delete_question("q001")

        # Reload from file
        manager2 = AdminQuestionManager(questions_file=temp_questions_with_data)
        assert manager2.get_question("q001") is None


class TestAnswerVerification:
    """Test answer verification with normalization."""

    def test_verify_correct_answer(self, manager):
        """Test verifying correct answer."""
        q = manager.create_question(
            category="personality",
            image_id="img_001",
            answer="Steve Jobs",
        )

        # Should handle case insensitivity
        assert manager.verify_answer(q["id"], "steve jobs") is True
        assert manager.verify_answer(q["id"], "STEVE JOBS") is True
        assert manager.verify_answer(q["id"], "Steve Jobs") is True

    def test_verify_incorrect_answer(self, manager):
        """Test verifying incorrect answer."""
        q = manager.create_question(
            category="personality",
            image_id="img_001",
            answer="Steve Jobs",
        )

        assert manager.verify_answer(q["id"], "Bill Gates") is False

    def test_verify_answer_nonexistent_question(self, manager):
        """Test verifying answer for non-existent question."""
        result = manager.verify_answer("q999", "Any Answer")
        assert result is False


class TestQuestionValidation:
    """Test question structure validation."""

    def test_validate_complete_question(self, manager_with_data):
        """Test validating a complete question."""
        q = manager_with_data.get_question("q001")
        is_valid, errors = manager_with_data.validate_question_structure(q)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_question_missing_field(self, manager_with_data):
        """Test validation detects missing fields."""
        q = manager_with_data.get_question("q001")
        del q["answer_hash"]

        is_valid, errors = manager_with_data.validate_question_structure(q)

        assert is_valid is False
        assert "answer_hash" in str(errors)

    def test_validate_question_invalid_difficulty(self, manager_with_data):
        """Test validation detects invalid difficulty."""
        q = manager_with_data.get_question("q001")
        q["difficulty"] = "impossible"

        is_valid, errors = manager_with_data.validate_question_structure(q)

        assert is_valid is False


class TestStatistics:
    """Test statistics generation."""

    def test_get_statistics_initial(self, manager):
        """Test statistics on empty manager."""
        stats = manager.get_statistics()

        assert stats["total_questions"] == 0
        assert stats["by_category"] == {}
        assert stats["by_difficulty"] == {}

    def test_get_statistics_with_data(self, manager_with_data):
        """Test statistics with data."""
        stats = manager_with_data.get_statistics()

        assert stats["total_questions"] == 2
        assert "personality" in stats["by_category"]
        assert "logo" in stats["by_category"]
        assert stats["by_category"]["personality"] == 1
        assert stats["by_category"]["logo"] == 1
        assert stats["by_difficulty"]["easy"] == 1
        assert stats["by_difficulty"]["medium"] == 1


class TestImportExport:
    """Test import/export functionality."""

    def test_export_questions(self, manager_with_data, tmp_path):
        """Test exporting questions."""
        export_file = str(tmp_path / "exported.json")
        result = manager_with_data.export_questions(export_file)

        assert Path(export_file).exists()
        with open(export_file, "r") as f:
            data = json.load(f)
            assert data["total_questions"] == 2
            assert "questions" in data
            assert "export_date" in data

    def test_import_questions(self, manager_with_data, tmp_path):
        """Test importing questions with full data."""
        # Manually create an import file with full question data (including hashes)
        # In real scenario, this would be exported from another instance with data
        import_data = {
            "questions": [
                {
                    "id": "q999",
                    "category": "hardware",
                    "image_id": "img_999",
                    "answer_hash": "newhash123",
                    "answer_salt": "newsalt456",
                    "answer_length": 3,
                    "difficulty": "hard",
                    "description": "Imported question",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                },
            ]
        }
        
        import_file = str(tmp_path / "import.json")
        with open(import_file, "w") as f:
            json.dump(import_data, f)

        # Import to existing manager
        initial_count = len(manager_with_data.get_all_questions())
        imported_count = manager_with_data.import_questions(import_file)

        assert imported_count == 1
        assert len(manager_with_data.get_all_questions()) == initial_count + 1

    def test_import_duplicate_questions_skipped(self, manager_with_data, tmp_path):
        """Test that duplicate questions are not re-imported."""
        export_file = str(tmp_path / "export.json")
        manager_with_data.export_questions(export_file)

        # Import again - should skip existing
        imported_count = manager_with_data.import_questions(export_file)

        assert imported_count == 0
        assert len(manager_with_data.get_all_questions()) == 2

    def test_import_nonexistent_file_raises_error(self, manager):
        """Test importing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            manager.import_questions("/nonexistent/file.json")

    def test_import_invalid_format_raises_error(self, manager, tmp_path):
        """Test importing invalid file format raises error."""
        invalid_file = str(tmp_path / "invalid.json")
        with open(invalid_file, "w") as f:
            json.dump({"wrong_key": []}, f)

        with pytest.raises(ValueError):
            manager.import_questions(invalid_file)


class TestPersistence:
    """Test persistence to disk."""

    def test_questions_persist_across_instances(self, temp_questions_file):
        """Test that questions persist when reloading manager."""
        manager1 = AdminQuestionManager(questions_file=temp_questions_file)
        manager1.create_question(
            category="personality",
            image_id="img_1",
            answer="Steve Jobs",
        )

        # Create new instance from same file
        manager2 = AdminQuestionManager(questions_file=temp_questions_file)
        questions = manager2.get_all_questions()

        assert len(questions) == 1
        assert questions[0]["category"] == "personality"

    def test_load_nonexistent_file_initializes_empty(self):
        """Test loading non-existent file creates empty cache."""
        manager = AdminQuestionManager(questions_file="/nonexistent/path/questions.json")
        assert len(manager.get_all_questions()) == 0
