"""
AI Engine — Model Training Script
Uses TF-IDF vectorization on waste descriptions + industry descriptions
to build a similarity matrix for waste-to-industry matchmaking.
"""
import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(SCRIPT_DIR, "..", "dataset", "waste_industry_dataset.csv")
MODEL_DIR = os.path.join(SCRIPT_DIR, "..", "models")


def train_model():
    """Train the TF-IDF model and save artifacts."""
    print("[INFO] Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    print(f"   Loaded {len(df)} records")

    # Group by industry — combine all waste descriptions per industry
    industries = df.groupby("industry_name").agg({
        "waste_description": lambda x: " ".join(x),
        "industry_description": "first",
    }).reset_index()

    print(f"   Found {len(industries)} unique industries")

    # Create combined text for each industry (waste descriptions + industry description)
    industries["combined_text"] = (
        industries["waste_description"] + " " + industries["industry_description"]
    )

    # Build TF-IDF vectorizer
    print("[INFO] Building TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),  # Unigrams and bigrams
        min_df=1,
        max_df=0.95,
    )
    tfidf_matrix = vectorizer.fit_transform(industries["combined_text"])
    print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"   Matrix shape: {tfidf_matrix.shape}")

    # Save model artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)

    vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.pkl")
    matrix_path = os.path.join(MODEL_DIR, "tfidf_matrix.pkl")
    industries_path = os.path.join(MODEL_DIR, "industries.pkl")

    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(matrix_path, "wb") as f:
        pickle.dump(tfidf_matrix, f)
    with open(industries_path, "wb") as f:
        pickle.dump(industries[["industry_name", "industry_description"]].to_dict("records"), f)

    print(f"\n[OK] Model trained and saved to {MODEL_DIR}/")
    print(f"   - vectorizer.pkl ({os.path.getsize(vectorizer_path)} bytes)")
    print(f"   - tfidf_matrix.pkl ({os.path.getsize(matrix_path)} bytes)")
    print(f"   - industries.pkl ({os.path.getsize(industries_path)} bytes)")

    return vectorizer, tfidf_matrix, industries


if __name__ == "__main__":
    train_model()
