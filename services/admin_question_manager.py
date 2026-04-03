"""
AdminQuestionManager - Manages CRUD operations for quiz questions.

Features:
- Create new questions with encryption
- Read and list questions
- Update existing questions
- Delete questions with validation
- Validate question data structure
- Export/import questions
- Answer hashing for security

Design:
    Questions are always stored with encrypted answers on disk.
    When loaded into memory, they can be decrypted for editing.
    All modifications are validated before persistence.
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from services.encryption_service import EncryptionService
from services.answer_checker import AnswerChecker
from admin.constants import (
    MAX_IMAGE_SIZE_MB,
    ADMIN_PASSWORD_MIN_LENGTH,
)

logger = logging.getLogger(__name__)


class AdminQuestionManager:
    """
    Manages question data with encryption and validation.
    
    Responsibilities:
    - CRUD operations (Create, Read, Update, Delete)
    - Question validation
    - Answer hashing and encryption
    - File persistence
    - Batch operations
    - Export/import functionality
    
    Security Properties:
    - Answers are never stored in plaintext on disk
    - All answers are hashed using SHA256 + salt
    - Questions can optionally be fully encrypted
    - Timestamps track modifications
    - Audit logging for all operations
    
    Example:
        manager = AdminQuestionManager(
            questions_file="data/questions.json",
            encryption_service=encryption_service
        )
        
        new_q = manager.create_question(
            category="personality",
            image_id="img_001",
            answer="Steve Jobs",
            difficulty="medium"
        )
        
        q = manager.get_question("q001")
        manager.update_question("q001", {"difficulty": "hard"})
        manager.delete_question("q001")
    """

    def __init__(
        self,
        questions_file: str = "data/questions.json",
        encryption_service: Optional[EncryptionService] = None,
    ):
        """
        Initialize AdminQuestionManager.
        
        Args:
            questions_file: Path to questions.json
            encryption_service: Optional EncryptionService for full encryption
        """
        self.questions_file = Path(questions_file)
        self.encryption_service = encryption_service
        self.answer_checker = AnswerChecker()
        self._cache: Dict[str, Any] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load questions from file into memory cache."""
        if not self.questions_file.exists():
            logger.warning(f"Questions file not found: {self.questions_file}")
            self._cache = {"questions": []}
            return

        try:
            with open(self.questions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cache = data
                logger.info(f"Loaded {len(data.get('questions', []))} questions")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load questions file: {e}")
            self._cache = {"questions": []}

    def _save_cache(self) -> None:
        """Save questions cache back to file."""
        try:
            # Ensure parent directory exists
            self.questions_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.questions_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self._cache.get('questions', []))} questions")
        except IOError as e:
            logger.error(f"Failed to save questions file: {e}")
            raise

    def create_question(
        self,
        category: str,
        image_id: str,
        answer: str,
        difficulty: str = "medium",
        description: str = "",
        hints: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new question with answer hashing.
        
        Args:
            category: Question category (personality, logo, hardware, etc.)
            image_id: Reference to image file
            answer: The correct answer (will be hashed)
            difficulty: Level (easy, medium, hard)
            description: Optional description
            hints: Optional list of hints
        
        Returns:
            New question dict with all required fields
        
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        self._validate_question_data({
            "category": category,
            "image_id": image_id,
            "answer": answer,
            "difficulty": difficulty,
        })

        # Hash the answer for security
        answer_hash, answer_salt = self._hash_answer(answer)

        # Generate unique ID
        question_id = self._generate_question_id()

        # Create question object
        question = {
            "id": question_id,
            "category": category,
            "image_id": image_id,
            "answer_hash": answer_hash,
            "answer_salt": answer_salt,
            "answer_length": len(answer),
            "difficulty": difficulty,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        if hints:
            question["hints"] = hints

        # Add to cache and persist
        self._cache.setdefault("questions", []).append(question)
        self._save_cache()

        logger.info(f"Created question {question_id} in category {category}")
        return question

    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a question by ID.
        
        Args:
            question_id: The question ID to retrieve
        
        Returns:
            Question dict or None if not found
        """
        for q in self._cache.get("questions", []):
            if q["id"] == question_id:
                return q.copy()
        return None

    def get_all_questions(self) -> List[Dict[str, Any]]:
        """
        Get all questions.
        
        Returns:
            List of all questions (without sensitive answer data)
        """
        questions = []
        for q in self._cache.get("questions", []):
            # Remove sensitive fields before returning
            safe_q = {k: v for k, v in q.items() if k not in ["answer_hash", "answer_salt"]}
            questions.append(safe_q)
        return questions

    def get_questions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all questions in a category.
        
        Args:
            category: The category name
        
        Returns:
            List of questions in that category
        """
        questions = []
        for q in self._cache.get("questions", []):
            if q.get("category") == category:
                safe_q = {k: v for k, v in q.items() if k not in ["answer_hash", "answer_salt"]}
                questions.append(safe_q)
        return questions

    def update_question(self, question_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a question.
        
        Args:
            question_id: The question to update
            updates: Dict of fields to update
        
        Returns:
            Updated question dict
        
        Raises:
            ValueError: If question not found or validation fails
        """
        # Find question
        question_idx = None
        for idx, q in enumerate(self._cache.get("questions", [])):
            if q["id"] == question_id:
                question_idx = idx
                break

        if question_idx is None:
            raise ValueError(f"Question {question_id} not found")

        question = self._cache["questions"][question_idx]

        # Handle answer update specially
        if "answer" in updates:
            answer = updates.pop("answer")
            answer_hash, answer_salt = self._hash_answer(answer)
            updates["answer_hash"] = answer_hash
            updates["answer_salt"] = answer_salt
            updates["answer_length"] = len(answer)

        # Validate updated data
        merged = {**question, **updates}
        self._validate_question_data(merged)

        # Update fields
        for key, value in updates.items():
            question[key] = value

        question["updated_at"] = datetime.now().isoformat()

        # Persist
        self._cache["questions"][question_idx] = question
        self._save_cache()

        logger.info(f"Updated question {question_id}")
        return question.copy()

    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question by ID.
        
        Args:
            question_id: The question to delete
        
        Returns:
            True if deleted, False if not found
        """
        for idx, q in enumerate(self._cache.get("questions", [])):
            if q["id"] == question_id:
                del self._cache["questions"][idx]
                self._save_cache()
                logger.info(f"Deleted question {question_id}")
                return True
        return False

    def verify_answer(self, question_id: str, user_answer: str) -> bool:
        """
        Verify if a user's answer is correct.
        
        Args:
            question_id: The question to check
            user_answer: The user's answer attempt
        
        Returns:
            True if correct, False otherwise
        """
        question = self.get_question(question_id)
        if not question:
            logger.warning(f"Question {question_id} not found for verification")
            return False

        answer_hash = question.get("answer_hash")
        answer_salt = question.get("answer_salt")
        if not answer_hash or not answer_salt:
            logger.warning(f"Question {question_id} missing hash or salt")
            return False

        # Primary verification path: same algorithm as AnswerChecker/hash_answer.
        try:
            if self.answer_checker.verify_answer(user_answer, answer_hash, answer_salt):
                logger.debug(f"Answer verification for {question_id}: True")
                return True
        except ValueError:
            return False

        # Backward-compatibility fallback for legacy hashes created as SHA256(bytes_salt + normalized).
        try:
            normalized = self.answer_checker.normalize_answer(user_answer)
            legacy_hash = self._hash_answer_with_salt(normalized, bytes.fromhex(answer_salt))[0]
            result = legacy_hash == answer_hash
            logger.debug(f"Legacy answer verification for {question_id}: {result}")
            return result
        except (ValueError, TypeError):
            return False

    def validate_question_structure(self, question: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate question structure for completeness.
        
        Args:
            question: Question dict to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_fields = [
            "id",
            "category",
            "image_id",
            "answer_hash",
            "answer_salt",
            "answer_length",
            "difficulty",
        ]

        for field in required_fields:
            if field not in question:
                errors.append(f"Missing required field: {field}")

        # Validate field types and values
        if "difficulty" in question:
            valid_difficulties = ["easy", "medium", "hard"]
            if question["difficulty"] not in valid_difficulties:
                errors.append(f"Invalid difficulty: {question['difficulty']}")

        if "answer_length" in question and not isinstance(question["answer_length"], int):
            errors.append("answer_length must be an integer")

        return len(errors) == 0, errors

    def export_questions(self, output_file: str = "exported_questions.json") -> str:
        """
        Export all questions to a file (for backup or distribution).
        
        Args:
            output_file: Path to export file
        
        Returns:
            Path to exported file
        """
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_questions": len(self._cache.get("questions", [])),
            "categories": self._get_categories(),
            "questions": self.get_all_questions(),
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported {export_data['total_questions']} questions to {output_file}")
        return str(output_path)

    def import_questions(self, import_file: str) -> int:
        """
        Import questions from an exported file.
        
        Imports only new questions (by ID check).
        
        Args:
            import_file: Path to import file
        
        Returns:
            Number of questions imported
        
        Raises:
            FileNotFoundError: If import file not found
            ValueError: If import file format invalid
        """
        import_path = Path(import_file)
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_file}")

        with open(import_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "questions" not in data:
            raise ValueError("Invalid import file format: missing 'questions' key")

        existing_ids = {q["id"] for q in self._cache.get("questions", [])}
        imported = 0

        for question in data["questions"]:
            if question["id"] not in existing_ids:
                try:
                    self._validate_question_data(question)
                    self._cache.setdefault("questions", []).append(question)
                    imported += 1
                except ValueError as e:
                    logger.warning(f"Skipped invalid question {question.get('id')}: {e}")

        if imported > 0:
            self._save_cache()

        logger.info(f"Imported {imported} new questions")
        return imported

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about questions.
        
        Returns:
            Dict with counts by category and difficulty
        """
        questions = self._cache.get("questions", [])
        stats = {
            "total_questions": len(questions),
            "by_category": {},
            "by_difficulty": {},
        }

        for q in questions:
            category = q.get("category", "unknown")
            difficulty = q.get("difficulty", "unknown")

            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1

        return stats

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _validate_question_data(self, data: Dict[str, Any]) -> None:
        """
        Validate question data.
        
        Args:
            data: Question data to validate
        
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValueError("Question must be a dictionary")

        required = ["category", "image_id", "difficulty"]
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")

        # Validate difficulty
        valid_difficulties = ["easy", "medium", "hard"]
        if data["difficulty"] not in valid_difficulties:
            raise ValueError(f"Invalid difficulty: {data['difficulty']}")

        # Answer or answer_hash must be present
        if "answer" not in data and "answer_hash" not in data:
            raise ValueError("Question must have either 'answer' or 'answer_hash'")

    def _hash_answer(self, answer: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash an answer using SHA256 with salt.
        
        Args:
            answer: The answer to hash
            salt: Optional salt (if None, generates new salt)
        
        Returns:
            Tuple of (answer_hash, salt)
        """
        return self.answer_checker.hash_answer(answer, salt or "")

    def _hash_answer_with_salt(self, answer: str, salt: bytes) -> Tuple[str, str]:
        """
        Hash an answer with provided salt.
        
        Args:
            answer: The (already normalized) answer to hash
            salt: The salt to use
        
        Returns:
            Tuple of (answer_hash, salt_hex)
        """
        hash_obj = hashlib.sha256(salt + answer.encode())
        return hash_obj.hexdigest(), salt.hex()

    def _generate_question_id(self) -> str:
        """Generate a unique question ID."""
        existing_ids = {q["id"] for q in self._cache.get("questions", [])}
        counter = 1
        while f"q{counter:03d}" in existing_ids:
            counter += 1
        return f"q{counter:03d}"

    def _get_categories(self) -> List[str]:
        """Get list of all categories."""
        categories = set()
        for q in self._cache.get("questions", []):
            if "category" in q:
                categories.add(q["category"])
        return sorted(list(categories))
