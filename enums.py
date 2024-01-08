from enum import Enum


# Represents a question's difficulty level.
class DifficultyLevel(Enum):
    EASY = 'easy'
    MODERATE = 'moderate'
    HARD = 'hard'


# Represents sort order while listing questions
class OrderDirection(Enum):
    ASC = 'asc'
    DESC = 'desc'
