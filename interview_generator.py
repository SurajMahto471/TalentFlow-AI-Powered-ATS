"""Rule-based interview question generator based on candidate skills."""

import random
from typing import List

from config import DEFAULT_INTERVIEW_QUESTIONS, INTERVIEW_QUESTIONS
from models import ParsedJobDescription, ParsedResume


def generate_interview_questions(
    candidate: ParsedResume,
    job: ParsedJobDescription,
    max_questions: int = 5,
) -> List[str]:
    """
    Generate interview questions tailored to candidate and job skills.

    Args:
        candidate: Parsed candidate resume.
        job: Parsed job description.
        max_questions: Maximum number of questions to return.

    Returns:
        List of interview questions.
    """
    relevant_skills = set(s.lower() for s in candidate.skills)
    relevant_skills.update(s.lower() for s in job.required_skills)

    questions: list[str] = []
    for skill in relevant_skills:
        bank = INTERVIEW_QUESTIONS.get(skill, [])
        if bank:
            questions.append(random.choice(bank))

    if len(questions) < max_questions:
        remaining = max_questions - len(questions)
        questions.extend(random.sample(
            DEFAULT_INTERVIEW_QUESTIONS,
            min(remaining, len(DEFAULT_INTERVIEW_QUESTIONS)),
        ))

    return questions[:max_questions]


def attach_interview_questions(
    candidate: ParsedResume,
    job: ParsedJobDescription,
) -> ParsedResume:
    """
    Populate interview questions on a candidate record.

    Args:
        candidate: Parsed candidate resume.
        job: Parsed job description.

    Returns:
        Updated candidate with interview_questions field set.
    """
    candidate.interview_questions = generate_interview_questions(candidate, job)
    return candidate
