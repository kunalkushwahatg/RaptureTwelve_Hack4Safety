-- SQLite Database Schema for Missing Persons System
-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS preliminary_uidb_reports;
DROP TABLE IF EXISTS unidentified_bodies;
DROP TABLE IF EXISTS missing_persons;

-- Table 1: Missing Persons
CREATE TABLE missing_persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pid TEXT UNIQUE NOT NULL,
    fir_number TEXT NOT NULL,
    police_station TEXT NOT NULL,
    reported_date TEXT NOT NULL,
    name TEXT,
    age INTEGER,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    height_cm INTEGER,
    build TEXT,
    hair_color TEXT,
    eye_color TEXT,
    distinguishing_marks TEXT,
    clothing_description TEXT,
    person_description TEXT,
    last_seen_date TEXT,
    last_seen_latitude REAL,
    last_seen_longitude REAL,
    last_seen_address TEXT,
    profile_photo TEXT,
    extra_photos TEXT,
    reporter_name TEXT,
    reporter_contact TEXT,
    additional_notes TEXT,
    status TEXT CHECK (status IN ('Open', 'Matched', 'Closed')) DEFAULT 'Open',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Table 2: Unidentified Bodies (Main UIDB Table)
CREATE TABLE unidentified_bodies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pid TEXT UNIQUE NOT NULL,
    case_number TEXT NOT NULL,
    police_station TEXT NOT NULL,
    reported_date TEXT NOT NULL,
    found_date TEXT NOT NULL,
    postmortem_date TEXT,
    estimated_age INTEGER,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    height_cm INTEGER,
    build TEXT,
    hair_color TEXT,
    eye_color TEXT,
    distinguishing_marks TEXT,
    clothing_description TEXT,
    person_description TEXT,
    found_latitude REAL,
    found_longitude REAL,
    found_address TEXT,
    profile_photo TEXT,
    extra_photos TEXT,
    cause_of_death TEXT,
    postmortem_report_url TEXT,
    dna_sample_collected INTEGER DEFAULT 0,
    dental_records_available INTEGER DEFAULT 0,
    fingerprints_collected INTEGER DEFAULT 0,
    additional_notes TEXT,
    status TEXT CHECK (status IN ('Open', 'Matched', 'Closed')) DEFAULT 'Open',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Table 3: Preliminary UIDB Reports (Before Postmortem)
CREATE TABLE preliminary_uidb_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pid TEXT UNIQUE NOT NULL,
    report_number TEXT NOT NULL,
    police_station TEXT NOT NULL,
    reported_date TEXT NOT NULL DEFAULT (datetime('now')),
    found_date TEXT NOT NULL,
    estimated_age INTEGER,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    height_cm INTEGER,
    build TEXT,
    hair_color TEXT,
    eye_color TEXT,
    distinguishing_marks TEXT,
    clothing_description TEXT,
    person_description TEXT,
    found_latitude REAL,
    found_longitude REAL,
    found_address TEXT,
    profile_photo TEXT,
    extra_photos TEXT,
    initial_notes TEXT,
    status TEXT CHECK (status IN ('Pending', 'Processed', 'Archived')) DEFAULT 'Pending',
    uidb_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (uidb_id) REFERENCES unidentified_bodies(id)
);

-- Create indexes for better query performance
CREATE INDEX idx_missing_persons_pid ON missing_persons(pid);
CREATE INDEX idx_missing_persons_status ON missing_persons(status);
CREATE INDEX idx_missing_persons_reported_date ON missing_persons(reported_date);

CREATE INDEX idx_unidentified_bodies_pid ON unidentified_bodies(pid);
CREATE INDEX idx_unidentified_bodies_status ON unidentified_bodies(status);
CREATE INDEX idx_unidentified_bodies_found_date ON unidentified_bodies(found_date);

CREATE INDEX idx_preliminary_uidb_pid ON preliminary_uidb_reports(pid);
CREATE INDEX idx_preliminary_uidb_status ON preliminary_uidb_reports(status);
CREATE INDEX idx_preliminary_uidb_uidb_id ON preliminary_uidb_reports(uidb_id);

-- Triggers for auto-updating updated_at timestamp
CREATE TRIGGER update_missing_persons_updated_at 
AFTER UPDATE ON missing_persons
FOR EACH ROW
BEGIN
    UPDATE missing_persons SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_unidentified_bodies_updated_at 
AFTER UPDATE ON unidentified_bodies
FOR EACH ROW
BEGIN
    UPDATE unidentified_bodies SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_preliminary_uidb_updated_at 
AFTER UPDATE ON preliminary_uidb_reports
FOR EACH ROW
BEGIN
    UPDATE preliminary_uidb_reports SET updated_at = datetime('now') WHERE id = NEW.id;
END;
