-- ============================================================
-- CSFMS Data Migration to Supabase
-- Source: Render PostgreSQL Backup (2026-11-10T20:25Z)
-- ============================================================

BEGIN;

-- Disable triggers & foreign keys temporarily during data restore
SET session_replication_role = 'replica';

-- Clear existing seed data
TRUNCATE TABLE "public"."roles", "public"."departments", "public"."programs", "public"."academic_years", "public"."sections", "public"."subjects", "public"."faculty", "public"."users", "public"."students", "public"."enrollments", "public"."faculty_assignments", "public"."attendance_sessions", "public"."attendance_records", "public"."institution_settings", "public"."audit_logs" CASCADE;

-- ------------------------------------------------------------
-- Table: roles (5 records)
-- ------------------------------------------------------------
INSERT INTO "public"."roles" ("id", "name", "description") VALUES (1, 'super_admin', 'Full system access');
INSERT INTO "public"."roles" ("id", "name", "description") VALUES (2, 'college_admin', 'College administrator / registrar');
INSERT INTO "public"."roles" ("id", "name", "description") VALUES (3, 'dept_head', 'Department head');
INSERT INTO "public"."roles" ("id", "name", "description") VALUES (4, 'faculty', 'Teaching faculty member');
INSERT INTO "public"."roles" ("id", "name", "description") VALUES (5, 'auditor', 'Read-only audit access');
SELECT setval(pg_get_serial_sequence('"public"."roles"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."roles"), 1), true);

-- ------------------------------------------------------------
-- Table: departments (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."departments" ("id", "code", "name", "description", "active", "created_at") VALUES (1, '1021', 'computer science and engineering', NULL, TRUE, '2026-10-11 20:24:38.325373');
INSERT INTO "public"."departments" ("id", "code", "name", "description", "active", "created_at") VALUES (2, 'CSE', 'Computer Science and Engineering', NULL, TRUE, '2026-10-19 02:32:34.501918');
SELECT setval(pg_get_serial_sequence('"public"."departments"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."departments"), 1), true);

-- ------------------------------------------------------------
-- Table: programs (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."programs" ("id", "code", "name", "duration_years", "department_id", "active", "created_at") VALUES (1, '1021', 'computer science', 4, 1, TRUE, '2026-10-11 20:25:11.00349');
INSERT INTO "public"."programs" ("id", "code", "name", "duration_years", "department_id", "active", "created_at") VALUES (2, 'BTECH-CSE', 'B.Tech - Computer Science and Engineering', 4, 2, TRUE, '2026-10-19 02:32:34.506362');
SELECT setval(pg_get_serial_sequence('"public"."programs"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."programs"), 1), true);

-- ------------------------------------------------------------
-- Table: academic_years (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."academic_years" ("id", "label", "start_date", "end_date", "active", "created_at") VALUES (1, '2025-2026', '2026-10-12', '2027-06-12', FALSE, '2026-10-11 20:25:45.154757');
INSERT INTO "public"."academic_years" ("id", "label", "start_date", "end_date", "active", "created_at") VALUES (2, '2025-26', '2025-07-01', '2026-06-30', TRUE, '2026-10-19 02:32:34.581424');
SELECT setval(pg_get_serial_sequence('"public"."academic_years"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."academic_years"), 1), true);

-- ------------------------------------------------------------
-- Table: sections (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."sections" ("id", "program_id", "academic_year_id", "semester", "section_name", "active", "created_at") VALUES (1, 1, 1, 5, 'B', TRUE, '2026-10-11 20:26:00.268582');
INSERT INTO "public"."sections" ("id", "program_id", "academic_year_id", "semester", "section_name", "active", "created_at") VALUES (2, 2, 2, 4, 'B', TRUE, '2026-10-19 02:32:34.588117');
SELECT setval(pg_get_serial_sequence('"public"."sections"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."sections"), 1), true);

-- ------------------------------------------------------------
-- Table: subjects (11 records)
-- ------------------------------------------------------------
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (4, '105401', 'Computer Organization & Architecture', 2, 4, 4, TRUE, '2026-10-19 02:32:34.692177');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (5, '105402', 'Formal Language and Automata Theory', 2, 4, 4, TRUE, '2026-10-19 02:32:34.6944');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (6, '105403', 'Design and Analysis of Algorithms', 2, 4, 4, TRUE, '2026-10-19 02:32:34.696201');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (7, '105404', 'Database Management System', 2, 4, 4, TRUE, '2026-10-19 02:32:34.697927');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (8, '105405', 'Effective Technical Communication', 2, 4, 3, TRUE, '2026-10-19 02:32:34.700243');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (9, '105406', 'Computer Networks', 2, 4, 4, TRUE, '2026-10-19 02:32:34.702325');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (10, '105407', 'NPTEL-I', 2, 4, 2, TRUE, '2026-10-19 02:32:34.777696');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (11, '105401P', 'Computer Organization & Architecture Lab', 2, 4, 2, TRUE, '2026-10-19 02:32:34.780265');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (12, '105403P', 'Design and Analysis of Algorithms Lab', 2, 4, 2, TRUE, '2026-10-19 02:32:34.782195');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (13, '105404P', 'Database Management System Lab', 2, 4, 2, TRUE, '2026-10-19 02:32:34.784075');
INSERT INTO "public"."subjects" ("id", "code", "title", "program_id", "semester", "credits", "active", "created_at") VALUES (14, '105406P', 'Computer Networks Lab', 2, 4, 2, TRUE, '2026-10-19 02:32:34.785827');
SELECT setval(pg_get_serial_sequence('"public"."subjects"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."subjects"), 1), true);

-- ------------------------------------------------------------
-- Table: faculty (7 records)
-- ------------------------------------------------------------
INSERT INTO "public"."faculty" ("id", "employee_id", "full_name", "department_id", "designation", "email", "phone", "qualification", "joining_date", "status", "created_at", "updated_at") VALUES (2, 'FAC001', 'Prof. Shweta Kumari', 2, 'Asst. Professor, CSE', NULL, NULL, NULL, NULL, 'active', '2026-10-19 02:32:34.595104', '2026-10-19 02:32:34.595108');
INSERT INTO "public"."faculty" ("id", "employee_id", "full_name", "department_id", "designation", "email", "phone", "qualification", "joining_date", "status", "created_at", "updated_at") VALUES (3, 'FAC002', 'Prof. Agam Kumar', 2, 'Asst. Professor, CSE', NULL, NULL, NULL, NULL, 'active', '2026-10-19 02:32:34.676937', '2026-10-19 02:32:34.676942');
INSERT INTO "public"."faculty" ("id", "employee_id", "full_name", "department_id", "designation", "email", "phone", "qualification", "joining_date", "status", "created_at", "updated_at") VALUES (4, 'FAC003', 'Prof. Krishnanand Mishra', 2, 'Asst. Professor, CSE', NULL, NULL, NULL, NULL, 'active', '2026-10-19 02:32:34.679923', '2026-10-19 02:32:34.679926');
INSERT INTO "public"."faculty" ("id", "employee_id", "full_name", "department_id", "designation", "email", "phone", "qualification", "joining_date", "status", "created_at", "updated_at") VALUES (5, 'FAC004', 'Prof. Abnish Ranjan', 2, 'Asst. Professor, CSE', NULL, NULL, NULL, NULL, 'active', '2026-10-19 02:32:34.682036', '2026-10-19 02:32:34.682038');
INSERT INTO "public"."faculty" ("id", "employee_id", "full_name", "department_id", "designation", "email", "phone", "qualification", "joining_date", "status", "created_at", "updated_at") VALUES (6, 'FAC005', 'Prof. Shauraya Ranjan', 2, 'Asst. Professor, CSE', NULL, NULL, NULL, NULL, 'active', '2026-10-19 02:32:34.684104', '2026-10-19 02:32:34.684107');
INSERT INTO "public"."faculty" ("id", "employee_id", "full_name", "department_id", "designation", "email", "phone", "qualification", "joining_date", "status", "created_at", "updated_at") VALUES (7, 'FAC006', 'Mr. Swagata Chakraborty', 2, 'GAP English', NULL, NULL, NULL, NULL, 'active', '2026-10-19 02:32:34.686271', '2026-10-19 02:32:34.686274');
INSERT INTO "public"."faculty" ("id", "employee_id", "full_name", "department_id", "designation", "email", "phone", "qualification", "joining_date", "status", "created_at", "updated_at") VALUES (8, 'FAC007', 'Mr. Hira Kumar Thakur', 2, 'Lab Assistant', NULL, NULL, NULL, NULL, 'active', '2026-10-19 02:32:34.688372', '2026-10-19 02:32:34.688374');
SELECT setval(pg_get_serial_sequence('"public"."faculty"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."faculty"), 1), true);

-- ------------------------------------------------------------
-- Table: users (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."users" ("id", "username", "email", "password_hash", "role_id", "active", "created_at", "last_login_at", "faculty_id") VALUES (1, 'admin', 'admin@college.edu', 'scrypt:32768:8:1$RWE5cTvDYSrHWflz$36ac7085eb49c09ac01ffaa3afcfecbf3797b4072dd842a43499789a0ae652db46aac13046448a5973c1109c93f53b39288e0c5c5264b7f342eb9768a8bb678c', 1, TRUE, '2026-10-11 20:20:46.664441', '2026-10-19 02:38:45.67795', NULL);
INSERT INTO "public"."users" ("id", "username", "email", "password_hash", "role_id", "active", "created_at", "last_login_at", "faculty_id") VALUES (2, 'superadmin', 'superadmin@college.edu', 'scrypt:32768:8:1$Eksgb69TI0qR4C3z$30f969f924fe0591714451d88901b2773b32fa4289dd9a60df709996d7f027d3fb763f6491d04968909e94c0b90ed549151b82b129296f15bf575e5bc51a49f7', 1, TRUE, '2026-10-11 20:20:47.363026', '2026-11-09 12:19:34.550472', NULL);
SELECT setval(pg_get_serial_sequence('"public"."users"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."users"), 1), true);

-- ------------------------------------------------------------
-- Table: students (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."students" ("id", "roll_number", "full_name", "program_id", "section_id", "email", "phone", "date_of_birth", "gender", "address", "admission_date", "status", "created_at", "updated_at") VALUES (2, 'DFDE', 'Yaduvanshi', 1, 1, 'innocentyadav100@gmail.com', '09241156709', NULL, 'Male', NULL, '2026-10-08', 'active', '2026-10-11 20:27:34.492286', '2026-10-11 20:27:34.49229');
INSERT INTO "public"."students" ("id", "roll_number", "full_name", "program_id", "section_id", "email", "phone", "date_of_birth", "gender", "address", "admission_date", "status", "created_at", "updated_at") VALUES (1, '10221', 'VISHWAJIT KUMAR', 2, 1, 'DARBHANGA619@GMAIL.COM', '09241156709', NULL, 'Male', NULL, '2026-10-02', 'active', '2026-10-11 20:27:07.064261', '2026-10-19 03:08:46.061906');
SELECT setval(pg_get_serial_sequence('"public"."students"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."students"), 1), true);

-- ------------------------------------------------------------
-- Table: enrollments (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."enrollments" ("id", "student_id", "section_id", "start_date", "end_date", "status") VALUES (1, 1, 1, '2026-10-02', NULL, 'active');
INSERT INTO "public"."enrollments" ("id", "student_id", "section_id", "start_date", "end_date", "status") VALUES (2, 2, 1, '2026-10-08', NULL, 'active');
SELECT setval(pg_get_serial_sequence('"public"."enrollments"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."enrollments"), 1), true);

-- ------------------------------------------------------------
-- Table: faculty_assignments (15 records)
-- ------------------------------------------------------------
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (2, 3, 2, 4, 2, '2026-10-19 02:32:34.790036');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (3, 6, 2, 5, 2, '2026-10-19 02:32:34.79693');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (4, 4, 2, 6, 2, '2026-10-19 02:32:34.799275');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (5, 5, 2, 7, 2, '2026-10-19 02:32:34.801447');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (6, 7, 2, 8, 2, '2026-10-19 02:32:34.803862');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (7, 2, 2, 9, 2, '2026-10-19 02:32:34.806368');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (8, 2, 2, 10, 2, '2026-10-19 02:32:34.808639');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (9, 3, 2, 11, 2, '2026-10-19 02:32:34.885557');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (10, 4, 2, 12, 2, '2026-10-19 02:32:34.9026');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (11, 5, 2, 13, 2, '2026-10-19 02:32:34.904848');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (12, 2, 2, 14, 2, '2026-10-19 02:32:34.906907');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (13, 8, 2, 11, 2, '2026-10-19 02:32:34.909025');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (14, 8, 2, 12, 2, '2026-10-19 02:32:34.91087');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (15, 8, 2, 13, 2, '2026-10-19 02:32:34.912683');
INSERT INTO "public"."faculty_assignments" ("id", "faculty_id", "section_id", "subject_id", "academic_year_id", "created_at") VALUES (16, 8, 2, 14, 2, '2026-10-19 02:32:34.914277');
SELECT setval(pg_get_serial_sequence('"public"."faculty_assignments"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."faculty_assignments"), 1), true);

-- ------------------------------------------------------------
-- Table: attendance_sessions (2 records)
-- ------------------------------------------------------------
INSERT INTO "public"."attendance_sessions" ("id", "section_id", "subject_id", "faculty_id", "session_date", "session_label", "status", "submitted_at", "created_at") VALUES (3, 2, 5, 6, '2026-10-19', '1', 'submitted', '2026-10-19 03:44:09.026511', '2026-10-19 03:07:14.811126');
INSERT INTO "public"."attendance_sessions" ("id", "section_id", "subject_id", "faculty_id", "session_date", "session_label", "status", "submitted_at", "created_at") VALUES (4, 2, 4, 3, '2026-11-09', '2', 'draft', NULL, '2026-11-09 12:21:36.612259');
SELECT setval(pg_get_serial_sequence('"public"."attendance_sessions"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."attendance_sessions"), 1), true);

-- ------------------------------------------------------------
-- Table: attendance_records (1 records)
-- ------------------------------------------------------------
INSERT INTO "public"."attendance_records" ("id", "session_id", "student_id", "status", "marked_by", "marked_at", "correction_note") VALUES (5, 3, 1, 'absent', 2, '2026-10-19 03:44:09.12034', NULL);
SELECT setval(pg_get_serial_sequence('"public"."attendance_records"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."attendance_records"), 1), true);

-- ------------------------------------------------------------
-- Table: institution_settings (1 records)
-- ------------------------------------------------------------
INSERT INTO "public"."institution_settings" ("id", "institution_name", "short_name", "address", "phone", "email", "website", "timezone", "attendance_edit_window_hours", "leave_counts_in_denominator", "academic_year_id") VALUES (1, 'Shri Phanishwar Nath Renu Engineering College, Araria', NULL, NULL, NULL, NULL, NULL, 'Asia/Kolkata', 24, FALSE, NULL);
SELECT setval(pg_get_serial_sequence('"public"."institution_settings"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."institution_settings"), 1), true);

-- ------------------------------------------------------------
-- Table: audit_logs (31 records)
-- ------------------------------------------------------------
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (1, 1, 'login', NULL, NULL, NULL, '10.31.197.151', '2026-10-11 20:21:11.954756');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (2, 1, 'logout', NULL, NULL, NULL, '10.27.198.133', '2026-10-11 20:23:53.705128');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (3, 1, 'login', NULL, NULL, NULL, '10.27.198.133', '2026-10-11 20:24:05.666534');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (4, 1, 'create', 'department', 1, 'Created dept 1021', '10.27.198.133', '2026-10-11 20:24:38.327363');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (5, 1, 'create', 'program', 1, 'Created program 1021', '10.31.197.151', '2026-10-11 20:25:11.005293');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (6, 1, 'create', 'student', 1, 'Added student 10221', '10.27.198.133', '2026-10-11 20:27:07.06623');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (7, 1, 'create', 'student', 2, 'Added student DFDE', '10.27.198.133', '2026-10-11 20:27:34.493635');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (8, 1, 'create', 'faculty', 1, 'Added faculty 14152', '10.27.198.133', '2026-10-11 20:28:33.367513');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (9, 1, 'create', 'faculty_assignment', 1, 'Assigned faculty 1 to section 1', '10.26.87.133', '2026-10-11 20:28:40.834767');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (10, 1, 'submit_attendance', 'attendance_session', 1, 'Session 2026-10-11 section=1', '10.27.198.133', '2026-10-11 20:28:56.271569');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (11, 1, 'submit_attendance', 'attendance_session', 2, 'Session 2026-10-11 section=1', '10.27.198.133', '2026-10-11 20:32:42.158387');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (12, 1, 'submit_attendance', 'attendance_session', 2, 'Session 2026-10-11 section=1', '10.27.198.133', '2026-10-11 20:32:55.358252');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (13, 1, 'lock', 'attendance_session', 2, 'Locked session 2026-10-11', '10.27.198.133', '2026-10-11 20:33:02.496531');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (14, 1, 'login', NULL, NULL, NULL, '10.31.197.151', '2026-10-12 07:25:59.671778');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (15, NULL, 'login_failed', NULL, NULL, 'username=admin ', '10.27.198.133', '2026-10-12 11:50:26.378114');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (16, 1, 'login', NULL, NULL, NULL, '10.24.124.2', '2026-10-19 01:11:40.499152');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (17, 1, 'login', NULL, NULL, NULL, '10.24.6.28', '2026-10-19 02:38:45.678087');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (18, 1, 'update_user', 'user', 2, 'Updated user superadmin active=True', '10.24.124.2', '2026-10-19 02:40:44.490563');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (19, 1, 'logout', NULL, NULL, NULL, '10.24.124.2', '2026-10-19 02:40:50.408248');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (20, 2, 'login', NULL, NULL, NULL, '10.26.96.152', '2026-10-19 02:41:06.385347');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (21, 2, 'delete', 'faculty', 1, 'Deleted faculty 14152 (ABNISHD) and associated sessions', '10.24.6.28', '2026-10-19 03:04:50.953131');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (22, 2, 'update', 'student', 1, 'Updated student 10221', '10.26.96.152', '2026-10-19 03:08:46.055832');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (23, 2, 'submit_attendance', 'attendance_session', 3, 'Session 2026-10-19 section=2', '10.26.96.152', '2026-10-19 03:44:09.026592');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (24, 2, 'logout', NULL, NULL, NULL, '10.26.96.152', '2026-10-19 12:40:25.175635');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (25, 2, 'login', NULL, NULL, NULL, '10.24.6.28', '2026-10-19 12:41:21.198064');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (26, 2, 'logout', NULL, NULL, NULL, '10.24.6.28', '2026-10-19 12:41:23.070917');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (27, 2, 'login', NULL, NULL, NULL, '10.24.124.2', '2026-10-19 12:41:30.700259');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (28, 2, 'login', NULL, NULL, NULL, '10.24.209.5', '2026-11-09 12:19:34.550579');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (29, 2, 'delete', 'subject', 1, 'Deleted subject 511 (DBMS)', '10.26.34.133', '2026-11-09 12:20:55.649743');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (30, 2, 'delete', 'subject', 3, 'Deleted subject 545 (TOC)', '10.26.34.133', '2026-11-09 12:21:02.192482');
INSERT INTO "public"."audit_logs" ("id", "actor_user_id", "action", "entity_type", "entity_id", "change_summary", "ip_address", "created_at") VALUES (31, 2, 'delete', 'subject', 2, 'Deleted subject 551 (COA)', '10.26.34.133', '2026-11-09 12:21:05.856227');
SELECT setval(pg_get_serial_sequence('"public"."audit_logs"', 'id'), COALESCE((SELECT MAX(id) FROM "public"."audit_logs"), 1), true);

SET session_replication_role = 'origin';

COMMIT;
