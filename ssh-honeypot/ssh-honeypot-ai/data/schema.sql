-- Custom tables for the AI pipeline.
-- NOTE: Cowrie's own tables (sessions, auth, input, downloads, ttylog, etc.)
-- are created separately by importing cowrie/docs/sql/mysql.sql -- see README.

CREATE TABLE IF NOT EXISTS classifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(32),
    input_id INT,
    command TEXT,
    label VARCHAR(50),
    severity VARCHAR(20),
    confidence FLOAT NULL,
    layer VARCHAR(20),
    mitre_id VARCHAR(20) NULL,
    mitre_name VARCHAR(100) NULL,
    reasoning TEXT NULL,
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS persistence_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(32),
    event_type VARCHAR(20),      -- 'command' or 'file_download'
    persistence_type VARCHAR(50),
    detail TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(32),
    summary TEXT,
    skill_level VARCHAR(20),
    intent VARCHAR(30),
    risk_score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS geoip_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(32),
    ip VARCHAR(45),
    country VARCHAR(100),
    city VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    looked_up_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
