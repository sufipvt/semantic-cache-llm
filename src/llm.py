
import os

from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Read the API key securely
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Check your .env file."
    )

# Initialize the Groq client
client = Groq(api_key=api_key)


def get_llm_response(question: str) -> str:
    """Send a question to Groq and return its answer."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the user's question clearly and concisely. "
                    "If you do not know the answer, say so."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
