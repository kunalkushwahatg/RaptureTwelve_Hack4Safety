-- MySQL Database Schema for Missing Persons System
-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS preliminary_uidb_reports;
DROP TABLE IF EXISTS unidentified_bodies;
DROP TABLE IF EXISTS missing_persons;

-- Table 1: Missing Persons
CREATE TABLE missing_persons (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique auto-incrementing ID
    pid VARCHAR(50) UNIQUE NOT NULL,  -- Unique person ID (e.g., MP-2024-00001)
    fir_number VARCHAR(50) NOT NULL,  -- FIR number from police report
    police_station VARCHAR(100) NOT NULL,  -- Name of the reporting police station
    reported_date DATETIME NOT NULL,  -- Date and time the missing report was filed
    name VARCHAR(100),  -- Full name of the missing person (if known)
    age INT,  -- Estimated or known age
    gender VARCHAR(20),  -- Gender
    height_cm INT,  -- Height in centimeters
    build VARCHAR(50),  -- Build (e.g., slim, athletic, heavy)
    hair_color VARCHAR(50),  -- Hair color
    eye_color VARCHAR(50),  -- Eye color
    distinguishing_marks TEXT,  -- Description of scars, tattoos, etc. (free text, unlimited)
    clothing_description TEXT,  -- Last worn clothing
    person_description TEXT,  -- Detailed physical description (unlimited text)
    last_seen_date DATETIME,  -- Date and time last seen
    last_seen_latitude DECIMAL(10, 8),  -- Geo-tag: Latitude of last seen location
    last_seen_longitude DECIMAL(11, 8),  -- Geo-tag: Longitude of last seen location
    last_seen_address VARCHAR(255),  -- Human-readable address of last seen location
    profile_photo VARCHAR(255),  -- Main profile photo path (e.g., "photos/missing_persons/MP-2024-00001/profile.jpg")
    extra_photos JSON,  -- Array of additional image paths (e.g., ["photo1.jpg", "photo2.jpg"]) for facial recognition
    reporter_name VARCHAR(100),  -- Name of the person reporting
    reporter_contact VARCHAR(50),  -- Phone/email of reporter
    additional_notes TEXT,  -- Any other details (e.g., medical conditions)
    status VARCHAR(20) DEFAULT 'Open',  -- Case status for analytics
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Record creation time
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- Last update time
    CONSTRAINT chk_gender_mp CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    CONSTRAINT chk_status_mp CHECK (status IN ('Open', 'Matched', 'Closed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 2: Unidentified Bodies (Main UIDB Table)
CREATE TABLE unidentified_bodies (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique auto-incrementing ID
    pid VARCHAR(50) UNIQUE NOT NULL,  -- Unique person ID (e.g., UIDB-2024-00001)
    case_number VARCHAR(50) NOT NULL,  -- Official case number assigned after postmortem
    police_station VARCHAR(100) NOT NULL,  -- Name of the police station handling the case
    reported_date DATETIME NOT NULL,  -- Date and time the case was officially filed
    found_date DATETIME NOT NULL,  -- Date and time the body was found
    postmortem_date DATETIME,  -- Date postmortem was conducted
    estimated_age INT,  -- Age determined from postmortem
    gender VARCHAR(20),  -- Gender determined from postmortem
    height_cm INT,  -- Height measured during postmortem
    build VARCHAR(50),  -- Build determined from examination
    hair_color VARCHAR(50),  -- Hair color
    eye_color VARCHAR(50),  -- Eye color
    distinguishing_marks TEXT,  -- Detailed description of scars, tattoos, etc. (unlimited)
    clothing_description TEXT,  -- Clothing found on body
    person_description TEXT,  -- Detailed physical description from postmortem (unlimited text)
    found_latitude DECIMAL(10, 8),  -- Geo-tag: Latitude where body was found
    found_longitude DECIMAL(11, 8),  -- Geo-tag: Longitude where body was found
    found_address VARCHAR(255),  -- Human-readable address where body was found
    profile_photo VARCHAR(255),  -- Main profile photo path (e.g., "photos/unidentified_bodies/UIDB-2024-00001/profile.jpg")
    extra_photos JSON,  -- Array of image paths from postmortem (e.g., ["photo1.jpg", "photo2.jpg"])
    cause_of_death TEXT,  -- Cause of death from postmortem report
    postmortem_report_url VARCHAR(255),  -- Path to full postmortem report document
    dna_sample_collected BOOLEAN DEFAULT FALSE,  -- Whether DNA sample was collected
    dental_records_available BOOLEAN DEFAULT FALSE,  -- Whether dental records are available
    fingerprints_collected BOOLEAN DEFAULT FALSE,  -- Whether fingerprints were collected
    additional_notes TEXT,  -- Any other forensic or investigative notes
    status VARCHAR(20) DEFAULT 'Open',  -- Case status
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Record creation time
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- Last update time
    CONSTRAINT chk_gender_uidb CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    CONSTRAINT chk_status_uidb CHECK (status IN ('Open', 'Matched', 'Closed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 3: Preliminary UIDB Reports (Before Postmortem)
CREATE TABLE preliminary_uidb_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique auto-incrementing ID
    pid VARCHAR(50) UNIQUE NOT NULL,  -- Unique person ID (e.g., PUIDB-2024-00001)
    report_number VARCHAR(50) NOT NULL,  -- Temporary report number assigned at discovery
    police_station VARCHAR(100) NOT NULL,  -- Name of the police station reporting
    reported_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Date and time the initial report was filed
    found_date DATETIME NOT NULL,  -- Date and time the body was found
    estimated_age INT,  -- Rough estimated age
    gender VARCHAR(20),  -- Apparent gender
    height_cm INT,  -- Rough estimated height in centimeters
    build VARCHAR(50),  -- Apparent build (e.g., slim, athletic, heavy)
    hair_color VARCHAR(50),  -- Hair color if visible
    eye_color VARCHAR(50),  -- Eye color if visible
    distinguishing_marks TEXT,  -- Initial notes on scars, tattoos, etc. (unlimited)
    clothing_description TEXT,  -- Clothing observed
    person_description TEXT,  -- Initial physical description (unlimited text)
    found_latitude DECIMAL(10, 8),  -- Geo-tag: Latitude where body was found
    found_longitude DECIMAL(11, 8),  -- Geo-tag: Longitude where body was found
    found_address VARCHAR(255),  -- Human-readable address where body was found
    profile_photo VARCHAR(255),  -- Main profile photo path (e.g., "photos/preliminary_uidb/PUIDB-2024-00001/profile.jpg")
    extra_photos JSON,  -- Array of initial image paths (e.g., ["photo1.jpg", "photo2.jpg"]) for quick facial recognition
    initial_notes TEXT,  -- Any immediate observations (e.g., apparent injuries, scene details)
    status VARCHAR(20) DEFAULT 'Pending',  -- Status: Pending postmortem, Processed (moved to main table)
    uidb_id INT,  -- Foreign key to link to full UIDB entry once postmortem is done (nullable)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Record creation time
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- Last update time
    CONSTRAINT chk_gender_puidb CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    CONSTRAINT chk_status_puidb CHECK (status IN ('Pending', 'Processed', 'Archived')),
    CONSTRAINT fk_uidb FOREIGN KEY (uidb_id) REFERENCES unidentified_bodies(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
