# 🛡️ PhishGuard — AI Email Phishing Detector

Applied AI × Cybersecurity. Detects phishing emails with a hybrid pipeline:
**TF-IDF text model + handcrafted heuristic features → Logistic Regression**,
served by a Flask web app with a full JSON API. Fully offline: no external APIs,
no cloud dependencies. Every prediction comes with **interpretable evidence**
(active heuristic features + top contributing text indicators).

Built for the **FutureTech HackFest 2026** — theme *"Innovating Tomorrow with
Emerging Technologies"* (focus areas: Applied AI, Cybersecurity).

## Results

| Metric | Holdout (20%) | 5-fold CV (combined) |
|---|---|---|
| Accuracy | 98.61% | 98.89% |
| Precision | 100.00% | 100.00% |
| Recall | 97.22% | 97.78% |
| F1 | 98.59% | 98.87% |

Holdout confusion matrix: **0 false positives, 2 false negatives** (144 test emails).

## Architecture

```
input email (text)
      │
      ├──► TF-IDF (1-2 grams, 1671 features) ─────────┐
      │                                               ├──► hstack ─► Logistic
      └──► 15 heuristic features (scaled) ────────────┘            Regression
                                                                      │
                                              verdict 0-100 + evidence ◄┘
```

- **`phishguard/build_dataset.py`** — deterministic generator (seed 42) of a
  balanced, labeled dataset (720 emails: 360 phishing / 360 legit) covering
  documented phishing patterns, including *hard* examples: legitimate emails
  that contain phishing-like words (verify/password/account) and low-intensity
  phishing. No real user data.
- **`phishguard/features.py`** — 15 interpretable heuristics: URL count, raw-IP
  URLs, typosquatting TLDs, click-here signals, urgency/financial keywords,
  generic greetings, ALL-CAPS ratio, attachment hints, Reply-To mismatch…
- **`phishguard/model.py`** — trains and saves `models/pipeline.joblib`.
- **`phishguard/evaluate.py`** — 5-fold CV + ablation study (text-only vs
  heuristics-only vs combined).
- **`app.py`** — Flask app: web UI + `POST /api/analyze` JSON API.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# (re)build dataset + retrain
.venv/bin/python -m phishguard.build_dataset
.venv/bin/python -m phishguard.model

# run tests
.venv/bin/python -m unittest tests.test_app

# serve
.venv/bin/python app.py            # http://127.0.0.1:5001
```

## API

```bash
curl -X POST http://127.0.0.1:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Subject: URGENT... full email text here ..."}'
```

Response: `score` (0-100), `label` (SAFE / SUSPICIOUS / PHISHING),
`active_features`, `top_indicators` — the *why*, not just the verdict.

## Honest limitations

- The training dataset is **synthetic** (pattern-based, curated, seed 42):
  cross-domain generalization to real-world mail traffic is not yet measured.
  Validation on public real datasets (e.g. Enron + labeled phishing corpora)
  is the next step.
- Text indicators shown are single-token contributions; future work will
  generate natural-language explanations (LLM-assisted, still offline-first).

## License

MIT
