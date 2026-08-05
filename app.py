"""
PhishGuard Flask web application.

Analyzes an email (pasted text) and returns a 0-100 phishing risk score,
a verdict label and interpretable evidence (active heuristic features +
top contributing text indicators).

Endpoints:
  GET  /                 -> web UI (paste email, analyze)
  POST /analyze          -> web UI result page
  POST /api/analyze      -> JSON API ({"text": "..."})
"""
import joblib
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, render_template, request
from scipy import sparse

from phishguard.features import HEURISTIC_NAMES, extract_heuristic_features

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)

_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = joblib.load(ROOT / "models" / "pipeline.joblib")
    return _pipeline


def _build_matrix(text, vectorizer, scaler):
    tfidf = vectorizer.transform([text])
    h = np.array(
        [[extract_heuristic_features(text)[n] for n in HEURISTIC_NAMES]],
        dtype=float,
    )
    h_scaled = scaler.transform(h)
    return sparse.hstack([tfidf, h_scaled]).tocsr(), tfidf


def analyze(text: str) -> dict:
    p = get_pipeline()
    model, vectorizer, scaler = p["model"], p["vectorizer"], p["scaler"]

    X, tfidf = _build_matrix(text, vectorizer, scaler)
    prob = float(model.predict_proba(X)[0][1])
    score = int(round(prob * 100))

    if score < 40:
        label, color, advice = "SAFE", "green", "No phishing signals detected."
    elif score < 65:
        label, color = "SUSPICIOUS", "orange"
        advice = "Mixed signals: check the sender before acting."
    else:
        label, color = "PHISHING", "red"
        advice = "High probability of phishing. Do not click links, do not reply."

    features = extract_heuristic_features(text)
    active = [
        (name, features[name])
        for name in HEURISTIC_NAMES
        if features[name] > 0
    ]

    # Top contributing text tokens (positive logistic coefficients * tfidf)
    coefs = model.coef_[0]
    feat_names = vectorizer.get_feature_names_out()
    contributions = []
    for idx, val in zip(tfidf.indices, tfidf.data):
        c = float(coefs[idx] * val)
        if c > 0.001:
            contributions.append((feat_names[idx], round(c, 4)))
    contributions.sort(key=lambda kv: -kv[1])
    top_indicators = contributions[:6]

    return {
        "score": score,
        "label": label,
        "color": color,
        "advice": advice,
        "active_features": active,
        "top_indicators": top_indicators,
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_view():
    text = request.form.get("email", "").strip()
    if not text:
        return render_template("index.html", error="Paste an email to analyze.")
    result = analyze(text)
    return render_template("index.html", result=result, email=text)


@app.route("/api/analyze", methods=["POST"])
def analyze_api():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "missing field 'text'"}), 400
    return jsonify(analyze(text))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
