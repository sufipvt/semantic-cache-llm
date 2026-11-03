import json
from pathlib import Path
from src.embeddings import generate_embedding

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVALUATION_FILE = PROJECT_ROOT / "data" / "evaluation.json"

def load_evaluation_data():
    with open(EVALUATION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def calculate_similarity(question1, question2):
    embedding1 = generate_embedding(question1)
    embedding2 = generate_embedding(question2)

    # Calculate cosine similarity
    similarity = embedding1 @ embedding2
    return float(similarity)  # Convert to float for JSON serialization

def evaluate_threshold(test_cases, threshold):

    true_hits = 0
    false_hits = 0
    false_misses = 0
    true_misses = 0

    for case in test_cases:

        similarity = calculate_similarity(
            case["cached_question"],
            case["test_question"]
        )

        predicted_match = similarity >= threshold
        expected_match = case["should_match"]

        if predicted_match and expected_match:
            true_hits += 1

        elif predicted_match and not expected_match:
            false_hits += 1

        elif not predicted_match and expected_match:
            false_misses += 1

        else:
            true_misses += 1

    total = len(test_cases)

    accuracy = (true_hits + true_misses) / total

    precision = (
        true_hits / (true_hits + false_hits)
        if true_hits + false_hits > 0 else 0
    )

    recall = (
        true_hits / (true_hits + false_misses)
        if true_hits + false_misses > 0 else 0
    )

    false_hit_rate = (
        false_hits / (false_hits + true_misses)
        if false_hits + true_misses > 0 else 0
    )

    return accuracy, precision, recall, false_hit_rate

if __name__ == "__main__":

    test_cases = load_evaluation_data()

    thresholds = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]

    print(f"Loaded {len(test_cases)} evaluation cases.\n")

    for threshold in thresholds:

        accuracy, precision, recall, false_hit_rate = (
            evaluate_threshold(test_cases, threshold)
        )

        print(f"THRESHOLD: {threshold}")

        print(f"Accuracy:       {accuracy:.2%}")
        print(f"Precision:      {precision:.2%}")
        print(f"Recall:         {recall:.2%}")
        print(f"False hit rate: {false_hit_rate:.2%}")

        print("-" * 45)