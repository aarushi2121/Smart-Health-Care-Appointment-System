
-- SmartCare Appointment Management System
-- File: 05_triggers.sql

CREATE OR REPLACE TRIGGER trg_validate_appointment
BEFORE INSERT OR UPDATE ON appointments
FOR EACH ROW
BEGIN
    -- Do not allow appointments in the past
    IF TRUNC(:NEW.appointment_date) < TRUNC(SYSDATE) THEN
        RAISE_APPLICATION_ERROR(
            -20010,
            'Appointment date cannot be in the past.'
        );
    END IF;

    -- Validate appointment time in HH24:MI format
    IF NOT REGEXP_LIKE(
        :NEW.appointment_time,
        '^([01][0-9]|2[0-3]):[0-5][0-9]$'
    ) THEN
        RAISE_APPLICATION_ERROR(
            -20011,
            'Appointment time must be in HH24:MI format.'
        );
    END IF;

    -- Validate status
    :NEW.status := UPPER(TRIM(:NEW.status));

    IF :NEW.status NOT IN (
        'WAITING',
        'IN PROGRESS',
        'COMPLETED',
        'CANCELLED'
    ) THEN
        RAISE_APPLICATION_ERROR(
            -20012,
            'Invalid appointment status.'
        );
    END IF;
END;
/

-- Verify trigger
SELECT trigger_name, status
FROM user_triggers
WHERE trigger_name = 'TRG_VALIDATE_APPOINTMENT';

