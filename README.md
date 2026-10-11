# College Student & Faculty Management System (CSFMS)

A Python-based web application for student records, faculty administration, daily classroom attendance, and reporting.

Built with **Python**, **Flask**, **SQLAlchemy**, and **Bootstrap 5**. Designed with a classic, traditional academic layout (navy & cream palette, serif typography: *Times New Roman*, *Georgia*, *Baskerville*) to reflect an institutional look and feel.

---

## Features (PRD v1.0 Baseline)

1. **Authentication & Role-Based Access Control (RBAC)**:
   - Super Admin, College Admin, Department Head, Faculty, and Auditor roles.
   - Secure password hashing with Werkzeug.
   - Server-side role enforcement on every route and form action.
2. **Academic Structure**:
   - Academic Departments, Programs / Degrees, Academic Years, Sections / Classes, and Subjects.
3. **Student Management**:
   - Student profiling (Roll Number, Full Name, Program, Section, Admission Date).
   - Unique Roll Number constraint per institutional policy.
   - Soft-archiving instead of hard deletion to preserve historical attendance.
   - Filtering and search by Roll Number, Name, Program, and Status.
4. **Faculty Administration & Teaching Allocations**:
   - Faculty profiling (Employee ID, Department, Designation, Contact Details).
   - Unique Employee ID enforcement.
   - Teaching allocations connecting Faculty to Section + Subject + Academic Year.
5. **Daily Attendance Register**:
   - Faculty can access only assigned classes/sections.
   - Daily status marking: **Present**, **Absent**, or **Leave**.
   - Mark-all shortcuts and draft save option.
   - Unique constraint `(section_id, subject_id, session_date, session_label)` preventing accidental duplicate registers.
   - Audit logging for corrections and register lock functionality.
6. **Reports & Exports**:
   - Attendance percentage report by section/subject/date range with color-coded badges (Green ≥ 75%, Amber ≥ 60%, Red < 60%).
   - Students list report by program and status.
   - CSV export with **OWASP Formula Injection Protection**.
7. **Audit & Accountability**:
   - Audit trail capturing actor, action, timestamp, entity, IP address, and change summary.
   - Passwords and sensitive tokens are strictly excluded from audit logs.

---

## Local Setup & Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- PowerShell (Windows) or Bash (Linux / macOS)

### 1. Clone & Enter Directory
```bash
git clone <repo-url>
cd epic-turing
```

### 2. Set Up Virtual Environment & Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
A pre-seeded SQLite database is created in `instance/csfms.db`. You can re-seed or initialize a fresh database with:
```powershell
.\.venv\Scripts\python.exe -c "
from app import create_app, db
app = create_app('development')
with app.app_context():
    db.create_all()
"
```

### 4. Default Seed Accounts
| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| **admin** | `Admin@123` | Super Admin | Full administrative access |
| **faculty1** | `Faculty@123` | Faculty | Linked to Dr. Alan Turing (CS501) |

### 5. Running the Application
```powershell
.\.venv\Scripts\python.exe run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## Running Automated Tests
```powershell
.\.venv\Scripts\pytest tests/
```
Tests cover:
- Authentication, session validation, and logout.
- Unique constraints on student Roll Number and faculty Employee ID.
- Prevention of duplicate attendance registers for the same section/subject/date.
- Role-based route authorization.
