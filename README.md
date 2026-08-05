# PhishGuard: AI Email Phishing Detector

Applied AI × Cybersecurity. Detects phishing emails with a hybrid pipeline:
**TF-IDF text model + handcrafted heuristic features → Logistic Regression**,
served by a Flask web app with a full JSON API. Fully offline: no external APIs,
no cloud dependencies. Every prediction comes with **interpretable evidence**
(active heuristic features + top contributing text indicators).

Built for the **FutureTech HackFest 2026** (theme *"Innovating Tomorrow with
Emerging Technologies"* (focus areas: Applied AI, Cybersecurity).

## Results

| Metric | Holdout (20%) | 5-fold CV (combined) |
|---|---|---|
| Accuracy | 98.61% | 98.75% |
| Precision | 100.00% | 100.00% |
| Recall | 97.22% | 97.50% |
| F1 | 98.59% | 98.73% |

Holdout confusion matrix: **0 false positives, 2 false negatives** (144 test emails).

## Architecture

```
input email (text)
      │
      ├──► TF-IDF (1-2 grams, 1677 features) ─────────┐
      │                                               ├──► hstack ─► Logistic
      └──► 15 heuristic features (scaled) ────────────┘            Regression
                                                                      │
                                              verdict 0-100 + evidence ◄┘
```

- **`phishguard/build_dataset.py`** is a deterministic generator (seed 42) of a
  balanced, labeled dataset (720 emails: 360 phishing / 360 legit) covering
  documented phishing patterns, including *hard* examples: legitimate emails
  that contain phishing-like words (verify/password/account) and low-intensity
  phishing. No real user data.
- **`phishguard/features.py`** provides 15 interpretable heuristics: URL count, raw-IP
  URLs, typosquatting TLDs, click-here signals, urgency/financial keywords,
  generic greetings, ALL-CAPS ratio, attachment hints, Reply-To mismatch…
- **`phishguard/model.py`** trains and saves `models/pipeline.joblib`.
- **`phishguard/evaluate.py`** runs 5-fold CV + ablation study (text-only vs
  heuristics-only vs combined).
- **`app.py`** is the Flask app: web UI + `POST /api/analyze` JSON API.

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
`active_features`, `top_indicators` (the *why*, not just the verdict).

## Honest limitations

- The training dataset is **synthetic** (pattern-based, curated, seed 42):
  cross-domain generalization to real-world mail traffic is not yet measured.
  Validation on public real datasets (e.g. Enron + labeled phishing corpora)
  is the next step.
- Text indicators shown are single-token contributions; future work will
  generate natural-language explanations (LLM-assisted, still offline-first).

## AI use disclosure

This project was developed with the assistance of generative AI tools
(AI-assisted coding, debugging and documentation support). All code was
executed, tested and verified locally; every metric reported in this
repository comes from running the code itself.

Disclosure framework:
- **Regulation (EU) 2024/1689 (EU AI Act), Article 50** (transparency
  obligations, applicable since 2 August 2026. Voluntarily applied (this is
  a research/educational open-source project, not an AI system placed on the
  market).
- **Italian Law No. 132 of 23 September 2025, Article 13** (information on
  AI use in clear, simple and exhaustive language.
- **EU Code of Practice on Transparency of AI-Generated Content** (final
  version, 10 June 2026).

The training dataset is fully synthetic and self-generated; no third-party
works, personal data or proprietary data were used. The application does not
collect, store or transmit personal data (offline by design, consistent with
GDPR principles).

## License

[MIT](LICENSE)

## Community

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
