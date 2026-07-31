# Maps our internal labels -> MITRE ATT&CK technique IDs
MITRE_MAP = {
    "recon":                 {"id": "T1082", "name": "System Information Discovery"},
    "download_payload":      {"id": "T1105", "name": "Ingress Tool Transfer"},
    "pipe_to_shell":         {"id": "T1059", "name": "Command and Scripting Interpreter"},
    "persistence_ssh_key":   {"id": "T1098.004", "name": "Account Manipulation: SSH Authorized Keys"},
    "persistence_cron":      {"id": "T1053.003", "name": "Scheduled Task/Job: Cron"},
    "destructive":           {"id": "T1485", "name": "Data Destruction"},
    "privilege_escalation":  {"id": "T1548", "name": "Abuse Elevation Control Mechanism"},
    "network_tool_install":  {"id": "T1588.002", "name": "Obtain Capabilities: Tool"},
    "history_clear":         {"id": "T1070.003", "name": "Indicator Removal: Clear Command History"},
    "shell_spawn":           {"id": "T1059.004", "name": "Command and Scripting Interpreter: Unix Shell"},
    # ML/LLM outputs use generic labels, map broadly
    "malicious":             {"id": "T1059", "name": "Command and Scripting Interpreter"},
    "suspicious":            {"id": "T1059", "name": "Command and Scripting Interpreter"},
    "benign":                {"id": None, "name": None},
}

def map_to_mitre(label: str):
    entry = MITRE_MAP.get(label, {"id": None, "name": None})
    return entry
