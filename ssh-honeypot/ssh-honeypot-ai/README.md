# SSH Honeypot with AI-Powered Attacker Profiling

A CDAC ITISS project combining the Cowrie SSH honeypot with a hybrid
AI pipeline (rule-based + trained ML + LLM fallback) for real-time
attacker command classification, MITRE ATT&CK technique mapping,
persistence detection, GeoIP-based geolocation, and AI-generated
attacker behavior summaries -- visualized in Grafana.

## Architecture

```
Cowrie (honeypot, port 2222, redirected from 22)
   -> MySQL (stores sessions, commands, downloads)
   -> 3-layer command classifier
        Layer 1: regex rules            (fast, free, deterministic)
        Layer 2: TF-IDF + RandomForest  (locally trained ML model)
        Layer 3: Google Gemini API      (LLM fallback for novel/obfuscated commands)
   -> MITRE ATT&CK technique mapping (static lookup table)
   -> File-change / persistence detection
        - real file drops in Cowrie's downloads/ folder (watchdog)
        - simulated command edits (authorized_keys, crontab, etc.)
   -> GeoIP enrichment (MaxMind GeoLite2, offline lookup)
   -> AI session summarizer (Gemini) - generates attacker intent,
      skill level, and risk score per session
   -> Grafana dashboards (reads MySQL directly via read-only user)
```

## Folder structure

```
ssh-honeypot-ai/
├── classifier/
│   ├── rules.py                 # Layer 1: regex rules
│   ├── mitre_map.py             # MITRE ATT&CK label -> technique ID lookup
│   ├── pipeline.py              # Combines all 3 layers + MITRE tagging
│   ├── ingest_and_classify.py   # Polls MySQL, classifies new commands, writes results
│   └── geoip_enrich.py          # Polls MySQL, enriches sessions with GeoIP data
├── ml_model/
│   ├── generate_seed_data.py    # Creates labeled training_data.csv
│   ├── train_model.py           # Trains TF-IDF + RandomForest, saves .joblib files
│   └── ml_classifier.py         # Layer 2: loads trained model for inference
├── llm_fallback/
│   └── llm_classifier.py        # Layer 3: Gemini API classification
├── summarizer/
│   └── summarizer.py            # Gemini-based session summarizer (attacker profiling)
├── file_monitor/
│   ├── persistence_rules.py     # Command-based persistence pattern detection
│   └── file_watcher.py          # Real-time watcher on Cowrie's downloads/ folder
├── data/
│   └── schema.sql               # Custom MySQL tables (classifications, persistence_events,
│                                 # session_summaries, geoip_data)
├── simulate_attacks.py          # Generates realistic test traffic via paramiko
├── cowrie-config/
│   └── cowrie.cfg.custom        # Only the Cowrie settings we changed from
│                                 # defaults (ssh port, hostname, output_mysql)
├── scripts/
│   ├── install_cowrie.sh        # Reference steps for installing Cowrie itself
│   └── setup_port_redirect.sh   # Reference steps for redirecting port 22 -> 2222
├── requirements.txt
├── .env.example                 # Template - copy to .env and fill in real values
└── .gitignore
```

> **Note on Cowrie itself:** Cowrie (github.com/cowrie/cowrie) is a
> separate, third-party open-source honeypot project -- it is a
> dependency of this project, not part of it, and is not included in
> this repo. Clone it separately per `scripts/install_cowrie.sh`, then
> apply the settings in `cowrie-config/cowrie.cfg.custom` to its config.

## Setup

1. Install and configure Cowrie separately (see `scripts/install_cowrie.sh`
   and cowrie.readthedocs.io), listening on port 2222, with real port 22
   redirected to it via iptables (`scripts/setup_port_redirect.sh`).
2. Import Cowrie's own schema: `mysql cowrie < cowrie/docs/sql/mysql.sql`
3. Import this project's tables: `mysql cowrie < data/schema.sql`
4. Create MySQL users:
   - `cowrie` (write) - used by Cowrie's own MySQL output plugin and by
     the pipeline scripts to write classification/persistence/summary results
   - `cowrie_ro` (read-only) - used by Grafana and by the read side of
     the pipeline scripts, so nothing can accidentally modify honeypot data
5. `cp .env.example .env` and fill in your real DB passwords and Gemini API key
6. `python3 -m venv venv && source venv/bin/activate`
7. `pip install -r requirements.txt`
8. Download MaxMind's free GeoLite2-City.mmdb into `data/geoip/` (requires
   a free MaxMind account + license key)
9. Run the four pipeline scripts (each in its own terminal, or as systemd
   services for production use):
   ```
   python3 classifier/ingest_and_classify.py
   python3 classifier/geoip_enrich.py
   python3 summarizer/summarizer.py
   python3 file_monitor/file_watcher.py
   ```
10. Connect Grafana to MySQL using the `cowrie_ro` user and build dashboards
    against the `sessions`, `classifications`, `persistence_events`,
    `session_summaries`, and `geoip_data` tables.

## AI components (what's actually AI vs. not)

| Component | AI? | Trained by us? | Purpose |
|---|---|---|---|
| Rules (Layer 1) | No | N/A | Fast regex pattern matching on obvious threats |
| RandomForest (Layer 2) | Yes | **Yes** | Statistical classification of command text via TF-IDF features |
| Gemini classifier (Layer 3) | Yes | No (API) | Reasoning-based classification of novel/obfuscated commands |
| Gemini summarizer | Yes | No (API) | Natural-language attacker profile generation per session |
| MITRE ATT&CK mapping | No | N/A | Static lookup table, standardizes AI output to industry taxonomy |
| GeoIP | No | N/A | Static offline database lookup |

## Notes

- `file_watcher.py` currently logs file-download persistence events with
  `session_id="unknown"` since Cowrie's filesystem watcher only sees
  filenames, not which session triggered the download. A future
  improvement would join against Cowrie's own `downloads` table to
  recover the session ID.
- The ML model is trained on a small seed dataset (`generate_seed_data.py`).
  For a stronger project deliverable, retrain periodically on real
  accumulated Cowrie session data as it grows.
