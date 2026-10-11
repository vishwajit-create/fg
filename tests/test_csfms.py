import unittest
from datetime import date
from app import create_app, db
from app.models import User, Role, Department, Program, AcademicYear, Section, Subject, Student, Faculty, FacultyAssignment, AttendanceSession, AttendanceRecord, Enrollment


class CSFMSStandardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        # Seed basic roles if not present
        for r in ['super_admin', 'college_admin', 'dept_head', 'faculty', 'auditor']:
            if not Role.query.filter_by(name=r).first():
                db.session.add(Role(name=r))
        db.session.commit()


        # Create Admin
        role_admin = Role.query.filter_by(name='super_admin').first()
        self.admin = User(username='testadmin', email='testadmin@college.edu', role_id=role_admin.id, active=True)
        self.admin.set_password('AdminPass123')
        db.session.add(self.admin)

        # Create Faculty
        dept = Department(code='TESTD', name='Test Dept')
        db.session.add(dept)
        db.session.commit()

        self.fac = Faculty(employee_id='FAC-999', full_name='Test Professor', department_id=dept.id, status='active')
        db.session.add(self.fac)
        db.session.commit()

        role_faculty = Role.query.filter_by(name='faculty').first()
        self.faculty_user = User(username='testfaculty', email='testfaculty@college.edu', role_id=role_faculty.id, faculty_id=self.fac.id, active=True)
        self.faculty_user.set_password('FacultyPass123')
        db.session.add(self.faculty_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_and_logout(self):
        # Valid login
        resp = self.client.post('/auth/login', data={'username': 'testadmin', 'password': 'AdminPass123'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Sign Out', resp.data)

        # Logout
        resp_logout = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(resp_logout.status_code, 200)
        self.assertIn(b'Sign In', resp_logout.data)

    def test_duplicate_roll_number(self):
        dept = Department.query.first()
        prog = Program(code='CS', name='CS Program', department_id=dept.id)
        db.session.add(prog)
        db.session.commit()

        s1 = Student(roll_number='ROLL001', full_name='Alice', program_id=prog.id, admission_date=date(2025, 1, 1), status='active')
        db.session.add(s1)
        db.session.commit()

        # Duplicate roll number
        s2 = Student(roll_number='ROLL001', full_name='Bob', program_id=prog.id, admission_date=date(2025, 1, 1), status='active')
        db.session.add(s2)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()

    def test_duplicate_employee_id(self):
        dept = Department.query.first()
        f1 = Faculty(employee_id='EMP001', full_name='Charlie', department_id=dept.id, status='active')
        db.session.add(f1)
        db.session.commit()

        # Duplicate employee ID
        f2 = Faculty(employee_id='EMP001', full_name='Diana', department_id=dept.id, status='active')
        db.session.add(f2)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()

    def test_unique_attendance_session(self):
        ay = AcademicYear(label='2025-26', start_date=date(2025, 1, 1), end_date=date(2025, 12, 31), active=True)
        dept = Department.query.first()
        prog = Program(code='PRG1', name='Program 1', department_id=dept.id)
        db.session.add_all([ay, prog])
        db.session.commit()

        sec = Section(program_id=prog.id, academic_year_id=ay.id, semester=1, section_name='A')
        sub = Subject(code='SUB1', title='Subject 1', program_id=prog.id)
        db.session.add_all([sec, sub])
        db.session.commit()

        sess1 = AttendanceSession(section_id=sec.id, subject_id=sub.id, faculty_id=self.fac.id, session_date=date(2025, 10, 1), session_label='1')
        db.session.add(sess1)
        db.session.commit()

        # Duplicate register on same section, subject, date, and label
        sess2 = AttendanceSession(section_id=sec.id, subject_id=sub.id, faculty_id=self.fac.id, session_date=date(2025, 10, 1), session_label='1')
        db.session.add(sess2)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()

    def test_role_based_access(self):
        # Faculty logs in
        self.client.post('/auth/login', data={'username': 'testfaculty', 'password': 'FacultyPass123'}, follow_redirects=True)
        # Attempting to access admin user accounts page should return 403
        resp = self.client.get('/admin/users')
        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
