"""
Efficient General Question Analyzer
Detects casual greetings and general questions to skip expensive context retrieval.

Performance optimizations:
- Uses compiled regex patterns for O(1) lookup
- Frozen sets for O(1) membership testing
- Early exit on first match
- No external API calls or heavy computation
"""

import re
from typing import Optional, Tuple


class GeneralQuestionAnalyzer:
    """
    Lightweight analyzer for detecting general questions and greetings.
    Designed for sub-millisecond response times.
    """

    # Frozen sets for O(1) lookups - significantly faster than lists
    SIMPLE_GREETINGS = frozenset({
        'hi', 'hello', 'hey', 'hola', 'greetings', 'howdy',
        'yo', 'sup', 'hiya', 'heya', 'bonjour', 'aloha'
    })

    WELL_BEING_QUESTIONS = frozenset({
        'how are you', 'how are you doing', "how're you", "how're you doing",
        'how do you do', 'what\'s up', 'whats up', 'wassup', "what's going on",
        'whats going on', 'how have you been', 'how\'s it going', 'hows it going',
        'how you doing', 'you good', 'you okay', 'how are things', 'how is it going'
    })

    IDENTITY_QUESTIONS = frozenset({
        'who are you', 'what are you', 'what is your name', 'whats your name',
        'what\'s your name', 'who r u', 'what r u', 'tell me about yourself',
        'introduce yourself'
    })

    # Compiled regex patterns for efficiency
    GREETING_PATTERN = re.compile(
        r'^(hi+|he+y+|hello+|hola+|yo+)[\s!.?]*$',
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize the analyzer with response templates."""
        self.response_templates = {
            'greeting': [
                "Hello! How can I help you with your knowledge base today?",
                "Hi there! What would you like to know from your knowledge base?",
                "Hey! I'm ready to help you explore your knowledge base.",
            ],
            'well_being': [
                "I'm doing great! I'm here to help you with your knowledge base. What can I answer for you?",
                "I'm excellent, thank you! Ready to assist you with any questions about your knowledge base.",
            ],
            'identity': [
                "I'm your Knowledge Base Assistant, powered by Supermemory and Claude. I help you find and understand information from your knowledge base. What would you like to know?",
                "I'm an AI assistant designed to help you explore your knowledge base using Supermemory's search capabilities and Claude's intelligence. How can I assist you today?",
            ],
        }

        # Track which response variation to use (simple round-robin)
        self._response_index = {'greeting': 0, 'well_being': 0, 'identity': 0}

    def analyze(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Analyze if the query is a general question.

        Args:
            query: The user's input query

        Returns:
            Tuple of (is_general_question: bool, response: Optional[str])
            - If is_general_question is True, response contains the suggested answer
            - If is_general_question is False, response is None

        Performance: Designed to complete in <1ms for most queries
        """
        if not query or not isinstance(query, str):
            return False, None

        # Normalize: strip whitespace, lowercase for comparison
        normalized = query.strip().lower()

        # Empty or very short queries that are just punctuation
        if not normalized or len(normalized) < 2:
            return False, None

        # Remove trailing punctuation for cleaner matching
        cleaned = normalized.rstrip('!?.,;')

        # Check 1: Simple single-word greetings (fastest check)
        if cleaned in self.SIMPLE_GREETINGS:
            return True, self._get_response('greeting')

        # Check 2: Regex pattern for greeting variations (hi!, heyyyy, etc)
        if self.GREETING_PATTERN.match(normalized):
            return True, self._get_response('greeting')

        # Check 3: Well-being questions
        if cleaned in self.WELL_BEING_QUESTIONS:
            return True, self._get_response('well_being')

        # Check 4: Identity questions
        if cleaned in self.IDENTITY_QUESTIONS:
            return True, self._get_response('identity')

        # Check 5: Compound greetings (e.g., "hi there", "hey buddy")
        # Only check first word to maintain performance
        first_word = cleaned.split()[0] if ' ' in cleaned else cleaned
        if first_word in self.SIMPLE_GREETINGS and len(cleaned.split()) <= 3:
            # Allow short greeting phrases like "hi there" or "hello friend"
            return True, self._get_response('greeting')

        # Not a general question - proceed with normal context retrieval
        return False, None

    def _get_response(self, category: str) -> str:
        """
        Get a response from the template, rotating through variations.

        Args:
            category: The category of response ('greeting', 'well_being', 'identity')

        Returns:
            A response string
        """
        templates = self.response_templates[category]
        index = self._response_index[category]
        response = templates[index]

        # Rotate to next response for variety
        self._response_index[category] = (index + 1) % len(templates)

        return response

    def is_likely_knowledge_query(self, query: str) -> bool:
        """
        Additional check: Does the query contain knowledge-seeking indicators?
        Can be used as a secondary filter.

        Args:
            query: The user's input query

        Returns:
            True if query contains knowledge-seeking keywords
        """
        if not query:
            return False

        knowledge_indicators = {
            'what', 'when', 'where', 'why', 'how', 'who', 'which',
            'explain', 'describe', 'tell me', 'find', 'search',
            'show', 'list', 'get', 'give', 'provide', 'details',
            'information', 'about', 'regarding', 'concerning'
        }

        query_lower = query.lower()
        return any(indicator in query_lower for indicator in knowledge_indicators)


# Singleton instance for reuse across requests
_analyzer_instance = None

def get_analyzer() -> GeneralQuestionAnalyzer:
    """
    Get or create the singleton analyzer instance.
    Reusing the instance avoids recreation overhead.
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = GeneralQuestionAnalyzer()
    return _analyzer_instance
