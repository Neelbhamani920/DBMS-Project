-- ============================================================
--  Hospital Management System — MySQL Database Setup
--  Run this file once to create all tables and sample data.
--  Usage:  mysql -u root -p < database.sql
-- ============================================================

-- 1. Create and select database
CREATE DATABASE IF NOT EXISTS hospital_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hospital_db;

-- ============================================================
--  TABLE: Departments
-- ============================================================
CREATE TABLE IF NOT EXISTS Departments (
    dept_id       INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    floor         VARCHAR(20),
    head_doctor_id INT DEFAULT NULL,  -- FK added later (circular ref)
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  TABLE: Doctors
-- ============================================================
CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id        INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(150) NOT NULL,
    specialization   VARCHAR(100),
    dept_id          INT,
    phone            VARCHAR(20),
    email            VARCHAR(150),
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES Departments(dept_id)
        ON DELETE SET NULL
);

-- Now we can add the head_doctor FK safely
ALTER TABLE Departments
    ADD CONSTRAINT fk_head_doctor
    FOREIGN KEY (head_doctor_id) REFERENCES Doctors(doctor_id)
    ON DELETE SET NULL;

-- ============================================================
--  TABLE: Patients
-- ============================================================
CREATE TABLE IF NOT EXISTS Patients (
    patient_id        INT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(150) NOT NULL,
    dob               DATE,
    blood_group       VARCHAR(5),
    gender            ENUM('Male','Female','Other') DEFAULT 'Male',
    phone             VARCHAR(20),
    emergency_contact VARCHAR(20),
    address           TEXT,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  TABLE: Beds
-- ============================================================
CREATE TABLE IF NOT EXISTS Beds (
    bed_id      INT AUTO_INCREMENT PRIMARY KEY,
    ward        VARCHAR(80) NOT NULL,
    bed_number  VARCHAR(20) NOT NULL,
    type        ENUM('General','ICU','Emergency','Private') DEFAULT 'General',
    is_occupied TINYINT(1) DEFAULT 0,
    UNIQUE KEY uq_bed (ward, bed_number)
);

-- ============================================================
--  TABLE: Admissions
-- ============================================================
CREATE TABLE IF NOT EXISTS Admissions (
    admission_id   INT AUTO_INCREMENT PRIMARY KEY,
    patient_id     INT NOT NULL,
    bed_id         INT NOT NULL,
    admitted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    discharged_at  DATETIME DEFAULT NULL,
    notes          TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        ON DELETE CASCADE,
    FOREIGN KEY (bed_id) REFERENCES Beds(bed_id)
        ON DELETE RESTRICT
);

-- ============================================================
--  TABLE: Appointments
-- ============================================================
CREATE TABLE IF NOT EXISTS Appointments (
    appt_id       INT AUTO_INCREMENT PRIMARY KEY,
    patient_id    INT NOT NULL,
    doctor_id     INT NOT NULL,
    scheduled_at  DATETIME NOT NULL,
    status        ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
    notes         TEXT,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
        ON DELETE CASCADE
);

-- ============================================================
--  TABLE: Medical_Records
-- ============================================================
CREATE TABLE IF NOT EXISTS Medical_Records (
    record_id    INT AUTO_INCREMENT PRIMARY KEY,
    patient_id   INT NOT NULL,
    doctor_id    INT NOT NULL,
    diagnosis    TEXT,
    prescription TEXT,
    notes        TEXT,
    record_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
        ON DELETE CASCADE
);

-- ============================================================
--  TABLE: Emergency_Cases
-- ============================================================
CREATE TABLE IF NOT EXISTS Emergency_Cases (
    emergency_id  INT AUTO_INCREMENT PRIMARY KEY,
    patient_id    INT NOT NULL,
    triage_level  TINYINT NOT NULL CHECK (triage_level BETWEEN 1 AND 5),
    arrival_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    symptoms      TEXT,
    status        ENUM('Active','Discharged','Admitted') DEFAULT 'Active',
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        ON DELETE CASCADE
);

-- ============================================================
--  TABLE: Lab_Tests
-- ============================================================
CREATE TABLE IF NOT EXISTS Lab_Tests (
    test_id     INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT NOT NULL,
    test_name   VARCHAR(150) NOT NULL,
    result      TEXT,
    tested_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        ON DELETE CASCADE
);

-- ============================================================
--  INDEXES  (for faster queries)
-- ============================================================
CREATE INDEX idx_appt_patient   ON Appointments(patient_id);
CREATE INDEX idx_appt_doctor    ON Appointments(doctor_id);
CREATE INDEX idx_appt_status    ON Appointments(status);
CREATE INDEX idx_patient_name   ON Patients(name);
CREATE INDEX idx_emergency_lvl  ON Emergency_Cases(triage_level, arrival_time);
CREATE INDEX idx_beds_occupied  ON Beds(is_occupied);
CREATE INDEX idx_admission_pat  ON Admissions(patient_id);

-- ============================================================
--  TRIGGER: Auto-mark bed as occupied on new admission
-- ============================================================
DELIMITER $$

CREATE TRIGGER trg_occupy_bed
AFTER INSERT ON Admissions
FOR EACH ROW
BEGIN
    UPDATE Beds SET is_occupied = 1 WHERE bed_id = NEW.bed_id;
END$$

-- Trigger: Free bed when patient is discharged
CREATE TRIGGER trg_free_bed
AFTER UPDATE ON Admissions
FOR EACH ROW
BEGIN
    IF NEW.discharged_at IS NOT NULL AND OLD.discharged_at IS NULL THEN
        UPDATE Beds SET is_occupied = 0 WHERE bed_id = NEW.bed_id;
    END IF;
END$$

DELIMITER ;

-- ============================================================
--  SAMPLE DATA
-- ============================================================

-- Departments
INSERT INTO Departments (name, floor) VALUES
    ('Cardiology',       '3rd Floor'),
    ('Neurology',        '4th Floor'),
    ('Orthopaedics',     '2nd Floor'),
    ('Emergency',        '1st Floor'),
    ('General Medicine', '1st Floor');

-- Doctors
INSERT INTO Doctors (name, specialization, dept_id, phone, email) VALUES
    ('Dr. Anjali Sharma',  'Cardiologist',    1, '9876543210', 'anjali@hospital.com'),
    ('Dr. Rohan Mehta',    'Neurologist',     2, '9123456789', 'rohan@hospital.com'),
    ('Dr. Priya Patel',    'Orthopaedic',     3, '9988776655', 'priya@hospital.com'),
    ('Dr. Suresh Kumar',   'Emergency Med',   4, '9001122334', 'suresh@hospital.com'),
    ('Dr. Meena Joshi',    'General Physician',5,'9765432100','meena@hospital.com');

-- Patients
INSERT INTO Patients (name, dob, blood_group, gender, phone, emergency_contact, address) VALUES
    ('Ravi Shah',       '1985-06-12', 'O+',  'Male',   '9000000001', '9000000002', 'Bhavnagar, Gujarat'),
    ('Sunita Patel',    '1992-11-30', 'A+',  'Female', '9000000003', '9000000004', 'Ahmedabad, Gujarat'),
    ('Kiran Desai',     '1975-03-22', 'B-',  'Male',   '9000000005', '9000000006', 'Surat, Gujarat'),
    ('Pooja Trivedi',   '2000-08-15', 'AB+', 'Female', '9000000007', '9000000008', 'Vadodara, Gujarat'),
    ('Harish Nair',     '1968-01-05', 'O-',  'Male',   '9000000009', '9000000010', 'Rajkot, Gujarat');

-- Beds
INSERT INTO Beds (ward, bed_number, type, is_occupied) VALUES
    ('Ward A', 'A-01', 'General',   0),
    ('Ward A', 'A-02', 'General',   1),
    ('Ward B', 'B-01', 'Private',   0),
    ('ICU',    'I-01', 'ICU',       1),
    ('ICU',    'I-02', 'ICU',       0),
    ('ER',     'E-01', 'Emergency', 0),
    ('ER',     'E-02', 'Emergency', 1);

-- Appointments
INSERT INTO Appointments (patient_id, doctor_id, scheduled_at, status, notes) VALUES
    (1, 1, '2025-07-15 09:00:00', 'Scheduled',  'Routine cardiac check'),
    (2, 2, '2025-07-15 10:30:00', 'Scheduled',  'Migraine follow-up'),
    (3, 3, '2025-07-14 11:00:00', 'Completed',  'Post-fracture review'),
    (4, 5, '2025-07-13 08:00:00', 'Completed',  'General checkup'),
    (5, 4, '2025-07-16 14:00:00', 'Scheduled',  'Chest pain evaluation');

-- Emergency Cases
INSERT INTO Emergency_Cases (patient_id, triage_level, symptoms, status) VALUES
    (5, 1, 'Severe chest pain, shortness of breath',   'Active'),
    (3, 2, 'Head injury after fall',                   'Active'),
    (1, 3, 'High fever and dehydration',               'Active');

-- ============================================================
--  USEFUL VIEWS  (optional but handy)
-- ============================================================

-- View: Active appointments with names
CREATE OR REPLACE VIEW vw_active_appointments AS
    SELECT
        a.appt_id,
        p.name        AS patient_name,
        d.name        AS doctor_name,
        d.specialization,
        a.scheduled_at,
        a.status,
        a.notes
    FROM Appointments a
    JOIN Patients p ON a.patient_id = p.patient_id
    JOIN Doctors  d ON a.doctor_id  = d.doctor_id
    WHERE a.status = 'Scheduled'
    ORDER BY a.scheduled_at;

-- View: Bed availability summary
CREATE OR REPLACE VIEW vw_bed_summary AS
    SELECT
        type,
        COUNT(*) AS total_beds,
        SUM(is_occupied)     AS occupied,
        SUM(1-is_occupied)   AS available
    FROM Beds
    GROUP BY type;

-- View: Emergency triage queue
CREATE OR REPLACE VIEW vw_emergency_queue AS
    SELECT
        e.emergency_id,
        p.name          AS patient_name,
        p.blood_group,
        e.triage_level,
        e.arrival_time,
        e.symptoms
    FROM Emergency_Cases e
    JOIN Patients p ON e.patient_id = p.patient_id
    WHERE e.status = 'Active'
    ORDER BY e.triage_level ASC, e.arrival_time ASC;

-- ============================================================
--  VERIFY
-- ============================================================
SELECT 'Setup complete!' AS status;
SELECT TABLE_NAME, TABLE_ROWS
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'hospital_db';
