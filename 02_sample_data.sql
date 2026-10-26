
-- ============================================
-- SmartCare Appointment Management System
-- File: 02_sample_data.sql
-- ============================================

SET SERVEROUTPUT ON;

-- --------------------------------------------
-- 1. Insert sample patient: Priya Sharma
-- --------------------------------------------

INSERT INTO patients (patient_id, patient_name, phone)
SELECT patient_seq.NEXTVAL,
       'Priya Sharma',
       '9876543210'
FROM dual
WHERE NOT EXISTS (
    SELECT 1
    FROM patients
    WHERE LOWER(patient_name) = LOWER('Priya Sharma')
      AND phone = '9876543210'
);

-- --------------------------------------------
-- 2. Insert sample patient: Rahul Sharma
-- --------------------------------------------

INSERT INTO patients (patient_id, patient_name, phone)
SELECT patient_seq.NEXTVAL,
       'Rahul Sharma',
       '9876501234'
FROM dual
WHERE NOT EXISTS (
    SELECT 1
    FROM patients
    WHERE LOWER(patient_name) = LOWER('Rahul Sharma')
      AND phone = '9876501234'
);

-- --------------------------------------------
-- 3. Keep existing doctors unchanged
-- --------------------------------------------
-- The 8 doctors already exist in the database.
-- No doctor INSERT statements are required.

-- --------------------------------------------
-- 4. Save changes
-- --------------------------------------------

COMMIT;

-- --------------------------------------------
-- 5. Display patient records
-- --------------------------------------------

PROMPT ===== PATIENT RECORDS =====

SELECT patient_id, patient_name, phone
FROM patients
ORDER BY patient_id;

-- --------------------------------------------
-- 6. Display doctor records
-- --------------------------------------------

PROMPT ===== DOCTOR RECORDS =====

SELECT doctor_id, doctor_name, specialization
FROM doctors
ORDER BY doctor_id;

-- --------------------------------------------
-- End of sample data script
-- --------------------------------------------
