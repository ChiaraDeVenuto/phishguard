"""
PhishGuard — honest evaluation (5-fold CV + ablation study).

Shows whether the combined pipeline (TF-IDF + heuristics) truly beats each
signal alone, using cross-validated metrics instead of a single split.
"""
import csv
import sys
from pathlib import Path

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phishguard.features import HEURISTIC_NAMES, extract_heuristic_features  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "data" / "dataset.csv"


def load_dataset(path: Path):
    texts, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(int(row["label"]))
    return texts, labels


def evaluate(X, y, name):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    accs, precs, recs, f1s = [], [], [], []
    for tr_idx, te_idx in skf.split(X, y):
        X_tr, X_te = X[tr_idx], X[te_idx]
        y_tr, y_te = np.array(y)[tr_idx], np.array(y)[te_idx]
        clf = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced", random_state=42)
        clf.fit(X_tr, y_tr)
        preds = clf.predict(X_te)
        accs.append(accuracy_score(y_te, preds))
        precs.append(precision_score(y_te, preds))
        recs.append(recall_score(y_te, preds))
        f1s.append(f1_score(y_te, preds))
    print(f"{name:>18}  acc={np.mean(accs):.4f}  prec={np.mean(precs):.4f}  "
          f"rec={np.mean(recs):.4f}  f1={np.mean(f1s):.4f}")


def main():
    texts, y = load_dataset(DATA_CSV)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), max_features=4000, min_df=2, sublinear_tf=True, lowercase=True
    )
    X_tfidf = vectorizer.fit_transform(texts)

    h_raw = np.array(
        [[extract_heuristic_features(t)[n] for n in HEURISTIC_NAMES] for t in texts],
        dtype=float,
    )
    scaler = StandardScaler()
    X_h = scaler.fit_transform(h_raw)

    X_combined = sparse.hstack([X_tfidf, X_h]).tocsr()

    print("=== 5-fold CV (mean over folds) ===")
    evaluate(X_tfidf, y, "text-only (TF-IDF)")
    evaluate(X_h, y, "heuristics-only")
    evaluate(X_combined, y, "combined")


if __name__ == "__main__":
    main()
