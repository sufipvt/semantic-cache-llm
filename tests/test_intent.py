import pytest
from src.cache import classify_intent


@pytest.mark.parametrize(
    "question, expected",
    [
        ("What is machine learning?", "definition"),
        ("How does Redis work?", "definition"),
        ("How do I install Python?", "procedure"),
        ("How can I build a chatbot?", "procedure"),
        ("Compare Redis and MongoDB", "comparison"),
        ("Python vs Java", "comparison"),
        ("My Python code is not working", "troubleshooting"),
        ("How can I fix a Python error?", "troubleshooting"),
        ("Tell me about artificial intelligence", "general"),
        ("What happens when a cache expires?", "definition"),
    ],
)
def test_classify_intent(question, expected):
    assert classify_intent(question) == expected