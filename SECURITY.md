# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| main | Supported |

## Reporting a vulnerability

PhishGuard is a research/educational phishing detector. If you find a
security issue in the code, the dataset generator or the web app, please do
not open a public issue first. Report it privately via GitHub's
[Security Advisories](https://github.com/ChiaraDeVenuto/phishguard/security/advisories)
or by contacting the repository owner through GitHub.

You will receive an acknowledgment within 7 days, and a fix will be
coordinated before public disclosure where appropriate.

## Security notes for users

- PhishGuard is **not** a substitute for a production anti-phishing system.
  Its training corpus is synthetic and its real-world accuracy is not yet
  measured. Use the verdicts as a decision aid, not as an authoritative
  security control.
- The app runs locally by design and does not send email content anywhere.
- The model is deterministic and auditable: dataset generator, training
  pipeline and metrics are all committed to this repository.

## AI use disclosure

This project was developed with the assistance of generative AI tools
(AI-assisted coding, debugging and documentation support). All code was
executed, tested and verified locally; every metric reported comes from
running the code itself. This disclosure is made in line with Regulation
(EU) 2024/1689 (EU AI Act), Article 50 (transparency, applicable since
2 August 2026), Italian Law No. 132/2025, Article 13, and the EU Code of
Practice on Transparency of AI-Generated Content (10 June 2026). The training
dataset is fully synthetic and self-generated; the application does not
collect, store or transmit personal data.
