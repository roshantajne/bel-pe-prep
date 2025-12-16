from pydantic import BaseModel
from typing import List


class MCQ(BaseModel):
    question: str
    options: List[str]
    correct_option: int
    subject: str
    difficulty: str


class AnswerSubmission(BaseModel):
    selected_option: int
    correct_option: int
