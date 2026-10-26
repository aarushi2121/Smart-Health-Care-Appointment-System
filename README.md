
# SmartCare Appointment Management System

## Project Overview

SmartCare is an appointment management system
developed using Python Flask and Oracle Database.

Oracle SQL and PL/SQL are used to manage patients,
doctors, appointments, appointment tokens, and
appointment statuses.

## Technologies Used

- Python
- Flask
- Oracle Database
- SQL
- PL/SQL
- Oracle SQL Developer
- HTML and CSS

## Main Features

1. Patient record management
2. Doctor and specialization management
3. Appointment booking
4. Automatic appointment token generation
5. Appointment status management
6. Patient appointment count
7. Appointment date and time validation
8. Appointment reports and status summaries

## Project Files

- 01_create_tables.sql
- 02_sample_data.sql
- 03_procedures.sql
- 04_functions.sql
- 05_triggers.sql
- 06_test_queries.sql
- README.md

## Database Objects

### Tables
- PATIENTS
- DOCTORS
- APPOINTMENTS

### Stored Procedures
- BOOK_APPOINTMENT
- UPDATE_APPOINTMENT_STATUS

### Function
- COUNT_PATIENT_APPOINTMENTS

### Trigger
- TRG_VALIDATE_APPOINTMENT

## Setup Instructions

1. Install Oracle Database and SQL Developer.
2. Connect to the APPOINTMENT_APP schema.
3. Open 01_create_tables.sql and execute it.
4. Execute 02_sample_data.sql.
5. Execute 03_procedures.sql.
6. Execute 04_functions.sql.
7. Execute 05_triggers.sql.
8. Execute 06_test_queries.sql to test the project.

Use F5 (Run Script) in SQL Developer to execute
the scripts and view DBMS_OUTPUT messages.

## Important Notes

- Run the table script only when the tables do
  not already exist.
- Back up existing appointment data before making
  database structure changes.
- Sample records are for testing purposes.
- The Flask application and PL/SQL objects must
  use compatible table and column names.

## Conclusion

SmartCare demonstrates how Oracle SQL and PL/SQL
can be used to implement database tables,
relationships, stored procedures, functions,
triggers, validation, and reporting for an
appointment management system.
