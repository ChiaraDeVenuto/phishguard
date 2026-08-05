"""
PhishGuard — dataset builder.

Generates a curated, labeled synthetic dataset of phishing and legitimate
emails based on documented phishing patterns (APWG Phishing Activity Trends,
industry heuristics, common scam structures). Deterministic: fixed seed.

Output: data/dataset.csv  (columns: text, label, source)
label: 1 = phishing, 0 = legitimate
"""
import csv
import random
from pathlib import Path

SEED = 42
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

PHISH_URLS = [
    "http://paypa1-secure.com/verify/login",
    "http://pay-pal-verify.net/account/update",
    "http://amaz0n-update.com/confirm",
    "http://micros0ft-support.org/security",
    "http://goog1e-account.com/recovery",
    "http://wellsfargo-security.biz/verify",
    "http://185.220.101.4/login.php",
    "http://91.206.93.38/verify/index.php",
    "http://secure-bank-login.top/update",
    "http://account-verification.xyz/confirm",
    "http://apple-id-support.tk/verify",
    "http://netflix-billing-support.ml/update",
    "http://insta-gram-security.ga/confirm",
    "http://linkedin-alerts.club/recover",
    "http://dhl-parcel-update.icu/track",
    "http://fedex-delivery-notice.rest/track",
    "http://coinbase-wallet-verify.gq/claim",
    "http://steam-support.click/reward",
    "http://paypal-customer-support.loan/refund",
    "http://bank-of-america-alerts.work/verify",
]

LEGIT_DOMAINS = [
    "https://www.paypal.com", "https://www.amazon.com", "https://github.com",
    "https://www.linkedin.com", "https://mail.google.com", "https://www.airbnb.com",
    "https://www.spotify.com", "https://docs.python.org", "https://www.udemy.com",
    "https://www.coursera.org", "https://www.notion.so", "https://trello.com",
    "https://www.canva.com", "https://www.figma.com", "https://drive.google.com",
]

PHISH_SUBJECTS = [
    "URGENT: Your account has been suspended",
    "VERIFY YOUR ACCOUNT IMMEDIATELY",
    "Your payment was declined - action required",
    "Unusual login activity detected",
    "CONGRATULATIONS! You have won a prize",
    "Invoice #2093841 is overdue - pay now",
    "Your password will expire in 24 hours",
    "Confirm your identity to continue",
    "FINAL NOTICE: account closure",
    "Your package could not be delivered",
    "Limited time: 70% discount for you",
    "Security alert: new device login",
    "Your refund is pending - click to receive",
    "Update your billing information now",
    "ACCOUNT SUSPENDED DUE TO SUSPICIOUS ACTIVITY",
    "Claim your free gift card today!!!",
    "Wire transfer failed - resubmit details",
    "Your Netflix account has been compromised",
    "Action required: reactivate your account",
    "You are selected for a cash reward!!!",
]

LEGIT_SUBJECTS = [
    "Your order #48217 has shipped",
    "Weekly team update - projects on track",
    "Meeting agenda: Friday 14:30",
    "Your receipt from Amazon",
    "Invitation: Project kickoff next week",
    "Course enrollment confirmed: AI Practitioner",
    "Password change confirmation",
    "Newsletter: Tech Digest #42",
    "Interview schedule confirmed - 10:00 AM",
    "GitHub: new pull request in phonetics repo",
    "Your AWS certification results are ready",
    "Feedback survey - 2 minutes",
    "Team lunch on Friday",
    "Reminder: docs review tomorrow",
    "Your Cloud Practitioner certificate is available",
]

PHISH_OPENERS = [
    "Dear Customer,",
    "Dear User,",
    "Dear Valued Member,",
    "Dear Account Holder,",
]

PHISH_PREMISES = [
    "Due to unusual activity, your account has been temporarily suspended. Please verify your identity at: {url}",
    "Someone tried to access your account from a new device. Confirm it was you: {url}",
    "Your most recent payment could not be processed. Update your billing details at: {url}",
    "You have been selected for a reward. Claim it before it expires: {url}",
    "Your invoice remains unpaid. Settle it now to avoid late fees: {url}",
    "We detected a security issue with your account. Login and confirm: {url}",
    "Your package could not be delivered due to incorrect address. Update your details: {url}",
    "A withdrawal was attempted on your account. Stop it here: {url}",
]

PHISH_BAITS = [
    "Click here",
    "Click here to verify",
    "Verify now",
    "Update your account",
    "Login and confirm",
    "Claim your reward",
    "Resolve this issue",
    "Confirm your identity",
]

PHISH_THREATS = [
    "Please provide your password, credit card details and SSN for verification.",
    "Send your bank account number and PIN to complete the transfer.",
    "Provide your login credentials and date of birth to unlock your account.",
    "Reply with your full name, address, phone number and bank details.",
    "Enter your card number, expiry and CVV on the page.",
]

PHISH_URGENCIES = [
    "Failure to act within 24 hours will result in permanent closure of your account.",
    "This is the FINAL NOTICE. Immediate action is required.",
    "Your account will be locked permanently if you do not verify within 24 hours.",
    "Do not ignore this message. Your account access will be revoked.",
    "This matter requires your immediate attention.",
]

FAKE_SENDERS = [
    "support@paypal.com", "security@amazon.com", "billing@netflix.com",
    "helpdesk@microsoft.com", "service@apple.com", "accounts@wellsfargo.com",
]

FAKE_REPLY_TOS = [
    "verify@pay-pal-verify.net", "admin@secure-bank-login.top",
    "claims@account-verification.xyz", "support@paypa1-secure.com",
    "noreply@amaz0n-update.com",
]

PHISH_ATTACHMENTS = ["invoice_99821.zip", "payment_details.exe", "receipt.scr", "tracking_info.docm"]


def _gen_phishing_email(rng: random.Random) -> str:
    subject = rng.choice(PHISH_SUBJECTS)
    opener = rng.choice(PHISH_OPENERS)
    url = rng.choice(PHISH_URLS)
    premise = rng.choice(PHISH_PREMISES).format(url=url)
    bait = rng.choice(PHISH_BAITS)
    threat = rng.choice(PHISH_THREATS)
    urgent = rng.choice(PHISH_URGENCIES)
    fake_sender = rng.choice(FAKE_SENDERS)
    reply_to = rng.choice(FAKE_REPLY_TOS)
    attachment = rng.choice(PHISH_ATTACHMENTS)
    body = (
        f"{opener}\n\n"
        f"{premise}\n\n"
        f"{bait}: {url}{rng.choice([' !!!', ' !!', ''])}\n\n"
        f"{threat}\n\n"
        f"{urgent}\n\n"
        f"From: {fake_sender} | Reply-To: {reply_to}\n\n"
        f"Attachment: {attachment}\n\n"
        f"Best regards,\nCustomer Support Team"
    )
    return f"Subject: {subject}\n\n{body}"


LEGIT_BODIES = [
    "Your order #{order} has shipped and is expected to arrive on {day}. You can track it at {domain}.",
    "Attached is the agenda for our meeting on Friday at 14:30. Please review before the call.",
    "Thank you for your purchase. Your receipt is available at {domain}/receipts/order-{order}.",
    "The project is on track. Key milestones are documented in our shared folder: {domain}/projects/quarterly.",
    "Your enrollment in the course has been confirmed. Materials are available at {domain}/courses/ai-practitioner.",
    "We changed your account password as you requested. If this was not you, please contact our team at {domain}/help.",
    "Your AWS Cloud Practitioner certificate is now available for download at {domain}/certificates.",
    "The interview is confirmed for next week. You can join via {domain}/meet/interview-{order}.",
    "Please find the weekly digest attached. Highlights include the new feature release and the Q&A summary.",
    "Our support line is +39 06 555 0117 if you need assistance with your account.",
]

LEGIT_CLOSERS = [
    "Let me know if you have any questions.",
    "Happy to discuss further if needed.",
    "Looking forward to your feedback.",
    "Feel free to reach out anytime.",
    "Have a great day!",
]

LEGIT_ROLES = [
    "Project Manager", "HR Specialist", "Support Lead",
    "Account Manager", "Team Coordinator",
]

LEGIT_SENDERS = [
    "Marco Rossi", "Anna Bianchi", "Luca Verdi",
    "Sara Moretti", "John Miller",
]

LEGIT_COMPANIES = ["TechFlow Ltd", "Acme Corp", "StudioNova", "GreenPath srl", "DataWorks"]


def _gen_legit_email(rng: random.Random) -> str:
    subject = rng.choice(LEGIT_SUBJECTS)
    name = rng.choice(["Alex", "Jamie", "Taylor", "Morgan", "Jordan"])
    body_template = rng.choice(LEGIT_BODIES)
    body = body_template.format(
        order=rng.randint(10000, 99999),
        day=rng.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
        domain=rng.choice(LEGIT_DOMAINS),
    )
    body = (
        f"Dear {name},\n\n"
        f"{rng.choice(['I hope this message finds you well.', 'Hope you are having a good week.'])}\n\n"
        f"{body}\n\n"
        f"{rng.choice(LEGIT_CLOSERS)}\n\n"
        f"Best regards,\n{rng.choice(LEGIT_SENDERS)}\n"
        f"{rng.choice(LEGIT_COMPANIES)}\n{rng.choice(LEGIT_ROLES)}"
    )
    return f"Subject: {subject}\n\n{body}"


# ---------------------------------------------------------------------------
# Hard examples: phishing with low-intensity signals and legitimate emails
# that contain "phishing-like" words (verify/password/account) but are real.
# These keep the task from being trivially solvable by keyword matching alone.
# ---------------------------------------------------------------------------

HARD_PHISH_BODIES = [
    "Hello, we noticed your email was used to register on a new device. To keep your account active, please confirm your email address here: {url}",
    "Hi there, our records show your billing details need a quick update. Please review them at your earliest convenience: {url}",
    "Dear user, a document was shared with you. Open it to view: {url}",
    "Hello, your subscription will renew soon. Manage your plan here: {url}",
    "Hi, we are updating our records for all users. Please confirm your profile at {url}.",
    "Dear member, as part of our annual security review we ask you to reconfirm your email address at {url}.",
]

HARD_PHISH_SUBJECTS = [
    "Please confirm your email address",
    "Billing details update",
    "A document was shared with you",
    "Subscription renewal notice",
    "Annual security review",
    "Profile confirmation request",
]

HARD_LEGIT_BODIES = [
    "Hi Alex, to finish your registration please verify your email address by clicking this link: {domain}/verify/email. The link expires in 48 hours.",
    "Dear Ms. Morgan, your account password was recently changed. If this was not you, contact us at {domain}/help.",
    "Hello Taylor, we updated your account security settings as requested. You can review them at {domain}/settings/security.",
    "Hi Jamie, please confirm your new email address to keep receiving notifications: {domain}/confirm-email.",
    "Dear Alex, our system detected a login from a new device. If this was you, no action is needed. Otherwise, reset your password at {domain}/reset.",
    "Hello Morgan, your two-factor authentication was enabled successfully. Your backup codes are available at {domain}/backup-codes.",
]

HARD_LEGIT_SUBJECTS = [
    "Verify your email address",
    "Password changed confirmation",
    "Security settings updated",
    "Confirm your new email",
    "New device login detected",
    "Two-factor authentication enabled",
]


def _gen_hard_phishing_email(rng: random.Random) -> str:
    subject = rng.choice(HARD_PHISH_SUBJECTS)
    url = rng.choice(PHISH_URLS)
    body = rng.choice(HARD_PHISH_BODIES).format(url=url)
    sender = rng.choice(["noreply@paypal-support.com", "no-reply@amazon-security.net",
                         "updates@netflix-billing.com", "mail@dropbox-security.org"])
    return f"Subject: {subject}\n\nDear {rng.choice(['Customer', 'User', 'Member'])},\n\n{body}\n\nRegards,\n{sender}"


def _gen_hard_legit_email(rng: random.Random) -> str:
    subject = rng.choice(HARD_LEGIT_SUBJECTS)
    domain = rng.choice(LEGIT_DOMAINS)
    body = rng.choice(HARD_LEGIT_BODIES).format(domain=domain)
    return f"Subject: {subject}\n\n{body}\n\nBest regards,\n{rng.choice(LEGIT_SENDERS)}\n{rng.choice(LEGIT_COMPANIES)}\n{rng.choice(LEGIT_ROLES)}"


def main() -> None:
    rng = random.Random(SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    n_phishing, n_legit, n_hard_phish, n_hard_legit = 260, 260, 100, 100
    rows = []
    for _ in range(n_phishing):
        rows.append((_gen_phishing_email(rng), 1, "phishing_template"))
    for _ in range(n_legit):
        rows.append((_gen_legit_email(rng), 0, "legit_template"))
    for _ in range(n_hard_phish):
        rows.append((_gen_hard_phishing_email(rng), 1, "hard_phishing"))
    for _ in range(n_hard_legit):
        rows.append((_gen_hard_legit_email(rng), 0, "hard_legit"))
    rng.shuffle(rows)
    out = DATA_DIR / "dataset.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "source"])
        writer.writerows(rows)
    print(f"Dataset written: {out} ({len(rows)} emails, balanced)")


if __name__ == "__main__":
    main()
