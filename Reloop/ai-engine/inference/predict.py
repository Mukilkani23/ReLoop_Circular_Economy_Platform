"""
AI Engine — Inference Module
Loads the trained TF-IDF model and returns top-N industry recommendations
for a given waste description using cosine similarity.
"""
import os
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "..", "models")

# --- Load model artifacts ---
_vectorizer = None
_tfidf_matrix = None
_industries = None


def _load_model():
    """Lazy-load model artifacts."""
    global _vectorizer, _tfidf_matrix, _industries

    if _vectorizer is not None:
        return

    vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.pkl")
    matrix_path = os.path.join(MODEL_DIR, "tfidf_matrix.pkl")
    industries_path = os.path.join(MODEL_DIR, "industries.pkl")

    if not all(os.path.exists(p) for p in [vectorizer_path, matrix_path, industries_path]):
        raise FileNotFoundError(
            f"Model files not found in {MODEL_DIR}. Run 'python training/train_model.py' first."
        )

    with open(vectorizer_path, "rb") as f:
        _vectorizer = pickle.load(f)
    with open(matrix_path, "rb") as f:
        _tfidf_matrix = pickle.load(f)
    with open(industries_path, "rb") as f:
        _industries = pickle.load(f)


def get_recommendations(waste_description: str, top_n: int = 3) -> list:
    """
    Get top-N industry recommendations for a waste description.

    Args:
        waste_description: Text describing the waste material.
        top_n: Number of recommendations to return.

    Returns:
        List of dicts with 'industry', 'match_score', and 'description'.
    """
    _load_model()

    # Transform the input using the trained vectorizer
    query_vector = _vectorizer.transform([waste_description])

    # Calculate cosine similarity
    similarities = cosine_similarity(query_vector, _tfidf_matrix).flatten()

    # Get top-N indices sorted by similarity
    top_indices = similarities.argsort()[::-1][:top_n]

    recommendations = []
    for idx in top_indices:
        industry = _industries[idx]
        recommendations.append({
            "industry": industry["industry_name"],
            "match_score": round(float(similarities[idx]), 4),
            "description": industry["industry_description"],
        })

    return recommendations


if __name__ == "__main__":
    # Quick test
    test_queries = [
        "scrap metal and steel pieces",
        "plastic bottles and PET waste",
        "food waste from restaurant kitchen",
        "old computers and circuit boards",
        "used tires and rubber scrap",
    ]

    print("🔍 Testing AI Matchmaking Engine\n")
    for query in test_queries:
        print(f"Query: '{query}'")
        try:
            results = get_recommendations(query)
            for i, rec in enumerate(results, 1):
                print(f"  {i}. {rec['industry']} (Score: {rec['match_score']})")
                print(f"     {rec['description']}")
            print()
        except FileNotFoundError as e:
            print(f"  ⚠️  {e}\n")
