
-- SmartCare Appointment Management System
-- File: 04_functions.sql

CREATE OR REPLACE FUNCTION count_patient_appointments (
    p_patient_id IN NUMBER
)
RETURN NUMBER
AS
    v_total NUMBER;
BEGIN
    SELECT COUNT(*)
    INTO v_total
    FROM appointments
    WHERE patient_id = p_patient_id;

    RETURN v_total;
END;
/

-- Example: count appointments for each patient
SELECT
    patient_id,
    patient_name,
    count_patient_appointments(patient_id)
        AS total_appointments
FROM patients
ORDER BY patient_id;
