"""
PhishGuard — model training pipeline.

TF-IDF (text) + handcrafted heuristic features (scaled) -> Logistic Regression.
Stratified 80/20 split, class-balanced. Saves a single joblib pipeline.

Usage:  python phishguard/model.py
"""
import csv
import joblib
from pathlib import Path

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from phishguard.features import HEURISTIC_NAMES, extract_heuristic_features

ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "data" / "dataset.csv"
MODEL_DIR = ROOT / "models"


def load_dataset(path: Path):
    texts, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(int(row["label"]))
    return texts, labels


def build_heuristic_matrix(texts) -> np.ndarray:
    rows = [extract_heuristic_features(t) for t in texts]
    return np.array(
        [[r[name] for name in HEURISTIC_NAMES] for r in rows], dtype=float
    )


def main() -> None:
    texts, y = load_dataset(DATA_CSV)
    X_tr, X_te, y_tr, y_te = train_test_split(
        texts, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), max_features=4000, min_df=2,
        sublinear_tf=True, lowercase=True,
    )
    X_tfidf_tr = vectorizer.fit_transform(X_tr)
    X_tfidf_te = vectorizer.transform(X_te)

    scaler = StandardScaler()
    X_h_tr = scaler.fit_transform(build_heuristic_matrix(X_tr))
    X_h_te = scaler.transform(build_heuristic_matrix(X_te))

    X_tr_all = sparse.hstack([X_tfidf_tr, X_h_tr]).tocsr()
    X_te_all = sparse.hstack([X_tfidf_te, X_h_te]).tocsr()

    model = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced", random_state=42)
    model.fit(X_tr_all, y_tr)

    preds = model.predict(X_te_all)
    print("=== PhishGuard training report ===")
    print(f"Samples: train={len(X_tr)}  test={len(X_te)}")
    print(f"Accuracy : {accuracy_score(y_te, preds):.4f}")
    print(f"Precision: {precision_score(y_te, preds):.4f}")
    print(f"Recall   : {recall_score(y_te, preds):.4f}")
    print(f"F1       : {f1_score(y_te, preds):.4f}")
    print("Confusion matrix [[TN FP], [FN TP]]:")
    print(confusion_matrix(y_te, preds))
    print(f"TF-IDF features: {X_tfidf_tr.shape[1]} + heuristics: {X_h_tr.shape[1]}")

    MODEL_DIR.mkdir(exist_ok=True)
    out = MODEL_DIR / "pipeline.joblib"
    joblib.dump(
        {
            "model": model,
            "vectorizer": vectorizer,
            "scaler": scaler,
            "heuristic_names": HEURISTIC_NAMES,
        },
        out,
    )
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
