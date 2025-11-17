"""Q&A extraction from podcast transcripts."""

from openai import AsyncOpenAI
import os
from typing import List, Dict


class QAExtractor:
    """Extract questions and answers from podcast content."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    async def extract(
        self,
        transcript: str,
        max_questions: int = 10
    ) -> List[Dict]:
        """
        Extract Q&A pairs from transcript.

        Args:
            transcript: Podcast transcript
            max_questions: Maximum number of Q&A pairs to extract

        Returns:
            List of Q&A pairs with metadata
        """
        prompt = f"""Analyze this podcast transcript and extract up to {max_questions} meaningful Q&A pairs.

For each Q&A:
1. Identify explicit questions asked
2. Extract implicit questions (topics discussed as if answering a question)
3. Provide clear, concise answers based on the discussion
4. Include context if needed

Format each Q&A as:
Q: [Question]
A: [Answer]
Context: [Optional context or timestamp reference]
---

Transcript:
{transcript[:6000]}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing conversations and extracting Q&A."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )

        content = response.choices[0].message.content
        qa_blocks = content.split('---')

        qa_pairs = []
        for block in qa_blocks:
            block = block.strip()
            if not block:
                continue

            question = ""
            answer = ""
            context = ""

            lines = block.split('\n')
            for line in lines:
                if line.startswith('Q:'):
                    question = line.replace('Q:', '').strip()
                elif line.startswith('A:'):
                    answer = line.replace('A:', '').strip()
                elif line.startswith('Context:'):
                    context = line.replace('Context:', '').strip()

            if question and answer:
                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "context": context,
                    "type": self._classify_question(question)
                })

        return qa_pairs[:max_questions]

    def _classify_question(self, question: str) -> str:
        """Classify question type."""
        question_lower = question.lower()

        if any(word in question_lower for word in ['how', 'how to']):
            return "how_to"
        elif any(word in question_lower for word in ['why', 'reason']):
            return "why"
        elif any(word in question_lower for word in ['what', 'which']):
            return "what"
        elif any(word in question_lower for word in ['when', 'time']):
            return "when"
        elif any(word in question_lower for word in ['where', 'location']):
            return "where"
        elif any(word in question_lower for word in ['who', 'person']):
            return "who"
        else:
            return "general"
