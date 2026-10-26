
-- SmartCare Appointment Management System
-- File: 03_procedures.sql

CREATE OR REPLACE PROCEDURE book_appointment (
    p_patient_id       IN NUMBER,
    p_doctor_id        IN NUMBER,
    p_appointment_date IN DATE,
    p_appointment_time IN VARCHAR2,
    p_reason           IN VARCHAR2
)
AS
    v_patient_name patients.patient_name%TYPE;
    v_token_number NUMBER;
BEGIN
    -- Check whether patient exists
    SELECT patient_name
    INTO v_patient_name
    FROM patients
    WHERE patient_id = p_patient_id;

    -- Check whether doctor exists
    DECLARE
        v_doctor_count NUMBER;
    BEGIN
        SELECT COUNT(*)
        INTO v_doctor_count
        FROM doctors
        WHERE doctor_id = p_doctor_id;

        IF v_doctor_count = 0 THEN
            RAISE_APPLICATION_ERROR(
                -20001, 'Doctor does not exist.'
            );
        END IF;
    END;

    -- Generate next token for this doctor and date
    SELECT NVL(MAX(token_number), 0) + 1
    INTO v_token_number
    FROM appointments
    WHERE doctor_id = p_doctor_id
      AND appointment_date >= TRUNC(p_appointment_date)
      AND appointment_date < TRUNC(p_appointment_date) + 1;

    -- Insert appointment
    INSERT INTO appointments (
        patient_id,
        patient_name,
        doctor_id,
        appointment_date,
        appointment_time,
        token_number,
        reason,
        status
    )
    VALUES (
        p_patient_id,
        v_patient_name,
        p_doctor_id,
        TRUNC(p_appointment_date),
        p_appointment_time,
        v_token_number,
        p_reason,
        'WAITING'
    );

    DBMS_OUTPUT.PUT_LINE(
        'Appointment booked successfully.'
    );
    DBMS_OUTPUT.PUT_LINE(
        'Generated token: ' || v_token_number
    );
END;
/

-- Procedure to update appointment status
CREATE OR REPLACE PROCEDURE update_appointment_status (
    p_appointment_id IN NUMBER,
    p_new_status     IN VARCHAR2
)
AS
BEGIN
    UPDATE appointments
    SET status = UPPER(TRIM(p_new_status))
    WHERE appointment_id = p_appointment_id;

    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(
            -20002, 'Appointment not found.'
        );
    END IF;

    DBMS_OUTPUT.PUT_LINE(
        'Appointment status updated successfully.'
    );
END;
/

-- Display procedures created in the schema
SELECT object_name, status
FROM user_objects
WHERE object_type = 'PROCEDURE'
  AND object_name IN (
      'BOOK_APPOINTMENT',
      'UPDATE_APPOINTMENT_STATUS'
  );
