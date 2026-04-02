"""
Unit tests for QuestionLoader service.
"""

import pytest
import json
import os
from services.question_loader import QuestionLoader
from models.question import Question


class TestQuestionLoader:
    """Tests for QuestionLoader."""
    
    @pytest.fixture
    def setup_test_data(self, tmp_path):
        """Setup test question data."""
        from services.answer_checker import AnswerChecker
        
        # Create hashes for test answers
        hash1, salt1 = AnswerChecker.hash_answer("Steve Jobs")
        hash2, salt2 = AnswerChecker.hash_answer("Google")
        hash3, salt3 = AnswerChecker.hash_answer("Python")
        
        questions_data = {
            "questions": [
                {
                    "id": "q1",
                    "image_id": "img_1",
                    "answer_hash": hash1,
                    "answer_salt": salt1,
                    "answer_length": 10,
                    "category": "IT Personalities",
                    "difficulty": "easy"
                },
                {
                    "id": "q2",
                    "image_id": "img_2",
                    "answer_hash": hash2,
                    "answer_salt": salt2,
                    "answer_length": 6,
                    "category": "Companies",
                    "difficulty": "easy"
                },
                {
                    "id": "q3",
                    "image_id": "img_3",
                    "answer_hash": hash3,
                    "answer_salt": salt3,
                    "answer_length": 6,
                    "category": "Programming",
                    "difficulty": "medium"
                }
            ]
        }
        
        # Write to temporary JSON file
        questions_file = tmp_path / "questions.json"
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)
        
        return str(questions_file)
    
    def test_initialization(self, setup_test_data):
        """Test QuestionLoader initialization."""
        loader = QuestionLoader(setup_test_data)
        # Private attribute: _questions
        assert loader._questions is None  # Not loaded yet
    
    def test_load_questions(self, setup_test_data):
        """Test loading questions from file."""
        loader = QuestionLoader(setup_test_data)
        questions = loader.load_all()
        
        assert len(questions) == 3
        assert all(isinstance(q, Question) for q in questions)
    
    def test_caching(self, setup_test_data):
        """Test that questions are cached."""
        loader = QuestionLoader(setup_test_data)
        
        questions1 = loader.load_all()
        questions2 = loader.load_all()
        
        # Should be same object (cached)
        assert questions1 is questions2
    
    def test_get_by_id(self, setup_test_data):
        """Test getting question by ID."""
        loader = QuestionLoader(setup_test_data)
        loader.load_all()
        
        question = loader.get_by_id("q1")
        assert question is not None
        assert question.id == "q1"
        # Note: answer is stored hashed, not plaintext
        assert question.answer_length == 10
        
        # Non-existent ID
        assert loader.get_by_id("q999") is None
    
    def test_get_by_category(self, setup_test_data):
        """Test getting questions by category."""
        loader = QuestionLoader(setup_test_data)
        loader.load_all()
        
        companies = loader.get_by_category("Companies")
        assert len(companies) == 1
        assert companies[0].id == "q2"
        
        # Empty category
        assert loader.get_by_category("NonExistent") == []
    
    def test_get_by_difficulty(self, setup_test_data):
        """Test getting questions by difficulty."""
        loader = QuestionLoader(setup_test_data)
        loader.load_all()
        
        easy = loader.get_by_difficulty("easy")
        assert len(easy) == 2
        
        medium = loader.get_by_difficulty("medium")
        assert len(medium) == 1
        
        # Empty difficulty
        assert loader.get_by_difficulty("hard") == []
    
    def test_get_random_question(self, setup_test_data):
        """Test getting random question."""
        loader = QuestionLoader(setup_test_data)
        loader.load_all()
        
        question = loader.get_random_question()
        assert question is not None
        assert isinstance(question, Question)
    
    def test_validate_all(self, setup_test_data):
        """Test validation of all questions."""
        loader = QuestionLoader(setup_test_data)
        loader.load_all()
        
        # Should not raise any errors
        loader.validate_all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
