-- ============================================================
-- Digital ID System — Full Database Schema Reference
-- Run AFTER Django migrations complete
-- ============================================================

USE digital_system_id;

SHOW TABLES;

DESCRIBE accounts_user;
DESCRIBE accounts_loginsession;
DESCRIBE employees_department;
DESCRIBE employees_designation;
DESCRIBE employees_employee;
DESCRIBE digital_id_digitalid;
DESCRIBE audit_auditlog;
DESCRIBE integrations_integrationlog;
DESCRIBE django_session;
