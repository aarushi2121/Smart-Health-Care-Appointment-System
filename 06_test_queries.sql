
-- SmartCare Appointment Management System
-- File: 06_test_queries.sql

SET SERVEROUTPUT ON;

-- 1. Display all patients
SELECT * FROM patients;

-- 2. Display all doctors
SELECT * FROM doctors;

-- 3. Display all appointments with patient and doctor names
SELECT
    a.appointment_id,
    a.patient_name,
    d.doctor_name,
    d.specialization,
    a.appointment_date,
    a.appointment_time,
    a.token_number,
    a.reason,
    a.status
FROM appointments a
JOIN doctors d
    ON a.doctor_id = d.doctor_id
ORDER BY a.appointment_date, a.token_number;

-- 4. Book a sample appointment
-- Uses the first available patient and doctor.
DECLARE
    v_patient_id NUMBER;
    v_doctor_id NUMBER;
BEGIN
    SELECT MIN(patient_id)
    INTO v_patient_id
    FROM patients;

    SELECT MIN(doctor_id)
    INTO v_doctor_id
    FROM doctors;

    IF v_patient_id IS NULL OR v_doctor_id IS NULL THEN
        RAISE_APPLICATION_ERROR(
            -20020,
            'Insert at least one patient and one doctor first.'
        );
    END IF;

    book_appointment(
        p_patient_id       => v_patient_id,
        p_doctor_id        => v_doctor_id,
        p_appointment_date => TRUNC(SYSDATE) + 1,
        p_appointment_time => '10:00',
        p_reason            => 'Routine check-up'
    );

    COMMIT;
END;
/

-- 5. Count appointments for each patient
SELECT
    patient_id,
    patient_name,
    count_patient_appointments(patient_id)
        AS total_appointments
FROM patients;

-- 6. Update the latest appointment status
-- Use a valid status such as WAITING or COMPLETED.
DECLARE
    v_appointment_id NUMBER;
BEGIN
    SELECT MAX(appointment_id)
    INTO v_appointment_id
    FROM appointments;

    IF v_appointment_id IS NOT NULL THEN
        update_appointment_status(
            v_appointment_id,
            'COMPLETED'
        );
        COMMIT;
    ELSE
        DBMS_OUTPUT.PUT_LINE(
            'No appointment is available to update.'
        );
    END IF;
END;
/

-- 7. Display appointment status summary
SELECT status, COUNT(*) AS total
FROM appointments
GROUP BY status
ORDER BY status;

-- 8. Display appointments for the next 7 days
SELECT *
FROM appointments
WHERE appointment_date >= TRUNC(SYSDATE)
  AND appointment_date < TRUNC(SYSDATE) + 7
ORDER BY appointment_date, token_number;
