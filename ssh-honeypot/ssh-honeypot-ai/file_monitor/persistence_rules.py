import re

# Sensitive paths/commands that indicate persistence attempts
PERSISTENCE_PATTERNS = [
    ("authorized_keys",  r"authorized_keys"),
    ("crontab_edit",     r"\b(crontab -e|crontab -l.*\|.*crontab -|/etc/cron)"),
    ("bashrc_profile",   r"\.(bashrc|bash_profile|profile)\b"),
    ("passwd_shadow",    r"/etc/(passwd|shadow)\b"),
    ("systemd_service",  r"/etc/systemd/system/.*\.service"),
    ("ssh_config",       r"/etc/ssh/sshd_config"),
    ("init_rc_local",    r"/etc/rc\.local"),
]

def detect_persistence(command: str):
    """
    Returns dict if command matches a known persistence pattern, else None.
    """
    cmd = command.strip()
    for label, pattern in PERSISTENCE_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return {"persistence_type": label, "matched_command": cmd}
    return None


if __name__ == "__main__":
    tests = [
        "echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys",
        "crontab -e",
        "nano ~/.bashrc",
        "cat /etc/passwd",
        "ls -la",
    ]
    for t in tests:
        print(t, "->", detect_persistence(t))
