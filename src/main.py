
import json
from pathlib import Path

from src.cache import add_to_cache, search_cache
from src.llm import get_llm_response

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FAQ_FILE = PROJECT_ROOT / "data" / "faqs.json"


def load_faqs():
    with open(FAQ_FILE, "r", encoding="utf-8") as file:
        faqs = json.load(file)

    for faq in faqs:
        add_to_cache(faq["question"], faq["answer"])

    print(f"Loaded {len(faqs)} FAQs into the cache.\n")

def get_answer(question: str):
    #search the cache for the answer
    cached_answer = search_cache(question)
    if cached_answer is not None:
        return cached_answer
    
    print("Calling Groq API...")

    try:
       answer = get_llm_response(question)

    except Exception as error:
       print(f"Groq API request failed: {error}")
       return "Sorry, I couldn't generate an answer. Please try again."

    # Cache only successful responses
    add_to_cache(question, answer)
    return answer



if __name__ == "__main__":
    load_faqs()

    while True:
        question = input("\nAsk a question (or type 'exit'): ").strip()

        if question.lower() == "exit":
            break

        if not question:
            print("Please enter a question.")
            continue

        answer = get_answer(question)
        print("\nAnswer:", answer)
