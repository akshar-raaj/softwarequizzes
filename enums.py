from enum import Enum


class DifficultyLevel(Enum):
    EASY = 'easy'
    MODERATE = 'moderate'
    HARD = 'hard'


class OrderDirection(Enum):
    ASC = 'asc'
    DESC = 'desc'
