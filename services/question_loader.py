"""
QuestionLoader - Loads questions from JSON data files.
Handles JSON parsing and question validation.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from models import Question


logger = logging.getLogger(__name__)


class QuestionLoader:
    """
    Loads quiz questions from JSON files.
    
    JSON Format:
    {
        "questions": [
            {
                "id": "q001",
                "image_id": "img_087",
                "answer_hash": "abc123...",
                "answer_salt": "salt456...",
                "answer_length": 10,
                "difficulty": "easy",
                "category": "personality"
            },
            ...
        ]
    }
    
    Example:
        >>> loader = QuestionLoader("data/questions.json")
        >>> questions = loader.load_all()
        >>> len(questions)
        25
        >>>
        >>> q = loader.get_by_id("q001")
        >>> q.category
        'personality'
    """
    
    def __init__(self, questions_file: str):
        """
        Initialize loader.
        
        Args:
            questions_file: Path to questions.json
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        self.questions_file = Path(questions_file)
        
        if not self.questions_file.exists():
            raise FileNotFoundError(f"Questions file not found: {questions_file}")
        
        self._questions: Optional[List[Question]] = None
        logger.debug(f"QuestionLoader initialized: {questions_file}")
    
    def load_all(self) -> List[Question]:
        """
        Load all questions from file.
        
        Returns:
            List of Question objects
            
        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If questions data is invalid
        """
        if self._questions is not None:
            return self._questions
        
        logger.info(f"Loading questions from {self.questions_file}")
        
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON in {self.questions_file}: {e}")
        
        if not isinstance(data, dict) or 'questions' not in data:
            raise ValueError("JSON must contain 'questions' key")
        
        questions_data = data['questions']
        if not isinstance(questions_data, list):
            raise ValueError("'questions' must be a list")
        
        # Convert to Question objects
        questions = []
        for q_data in questions_data:
            try:
                question = self._parse_question(q_data)
                questions.append(question)
            except ValueError as e:
                logger.warning(f"Skipping invalid question: {e}")
                continue
        
        self._questions = questions
        logger.info(f"Loaded {len(questions)} questions")
        
        return questions
    
    @staticmethod
    def _parse_question(q_data: dict) -> Question:
        """
        Parse question from dictionary.
        
        Args:
            q_data: Question data dictionary
            
        Returns:
            Question object
            
        Raises:
            ValueError: If required fields are missing/invalid
        """
        required = [
            'id', 'image_id', 'answer_hash', 'answer_salt',
            'answer_length', 'difficulty', 'category'
        ]
        
        missing = [field for field in required if field not in q_data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return Question(
            id=q_data['id'],
            image_id=q_data['image_id'],
            answer_hash=q_data['answer_hash'],
            answer_salt=q_data['answer_salt'],
            answer_length=q_data['answer_length'],
            difficulty=q_data['difficulty'],
            category=q_data['category'],
            description=q_data.get('description'),
        )
    
    def get_by_id(self, question_id: str) -> Optional[Question]:
        """
        Get question by ID.
        
        Args:
            question_id: Question ID (e.g., "q001")
            
        Returns:
            Question object, or None if not found
        """
        questions = self.load_all()
        for q in questions:
            if q.id == question_id:
                return q
        return None
    
    def get_by_category(self, category: str) -> List[Question]:
        """
        Get all questions in a category.
        
        Args:
            category: Category name (e.g., "personality")
            
        Returns:
            List of matching questions
        """
        questions = self.load_all()
        return [q for q in questions if q.category == category]
    
    def get_by_difficulty(self, difficulty: str) -> List[Question]:
        """
        Get all questions of a difficulty level.
        
        Args:
            difficulty: Difficulty level ("easy", "medium", "hard")
            
        Returns:
            List of matching questions
        """
        questions = self.load_all()
        return [q for q in questions if q.difficulty == difficulty]
    
    def get_random_question(self) -> Optional[Question]:
        """
        Get a random question.
        
        Returns:
            Random Question, or None if no questions
        """
        import secrets
        questions = self.load_all()
        if not questions:
            return None
        return secrets.choice(questions)
    
    def validate_all(self) -> bool:
        """
        Validate all loaded questions.
        
        Returns:
            True if all valid
            
        Raises:
            ValueError: If validation fails
        """
        questions = self.load_all()
        
        if not questions:
            raise ValueError("No questions loaded")
        
        # Check for duplicate IDs
        ids = [q.id for q in questions]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate question IDs found")
        
        logger.info(f"Validated {len(questions)} questions successfully")
        return True
