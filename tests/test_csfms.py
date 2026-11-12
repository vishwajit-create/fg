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
        ay = AcademicYear(label='TEST-YR', start_date=date(2025, 1, 1), end_date=date(2025, 12, 31), active=False)
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

    def test_batch_provision_and_mandatory_profile_setup(self):
        # Create an unlinked faculty member
        dept = Department.query.first()
        fac2 = Faculty(employee_id='FAC900', full_name='Lab Assistant Test', department_id=dept.id, status='active')
        db.session.add(fac2)
        db.session.commit()

        # Login as super_admin and run batch provisioning
        self.client.post('/auth/login', data={'username': 'testadmin', 'password': 'AdminPass123'}, follow_redirects=True)
        resp = self.client.post('/admin/users/provision-faculty', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'fac900', resp.data)

        provisioned_user = User.query.filter_by(username='fac900').first()
        self.assertIsNotNone(provisioned_user)
        self.assertTrue(provisioned_user.must_change_password)
        self.assertTrue(provisioned_user.has_pending_email())

        # Switch to provisioned user
        self.client.get('/auth/logout', follow_redirects=True)
        provisioned_user.set_password('TempPass@12')
        db.session.commit()

        login_resp = self.client.post('/auth/login', data={'username': 'fac900', 'password': 'TempPass@12'}, follow_redirects=False)
        self.assertEqual(login_resp.status_code, 302)
        self.assertIn('/auth/profile', login_resp.headers['Location'])

        # Guard should redirect /dashboard back to /auth/profile until setup complete
        dash_resp = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(dash_resp.status_code, 302)
        self.assertIn('/auth/profile', dash_resp.headers['Location'])

        # Complete profile with real email and new password
        prof_resp = self.client.post('/auth/profile', data={
            'email': 'lab.assistant@college.edu',
            'current_password': 'TempPass@12',
            'new_password': 'NewSecurePass@99',
            'confirm_password': 'NewSecurePass@99',
        }, follow_redirects=True)
        self.assertEqual(prof_resp.status_code, 200)
        self.assertIn(b'Sign Out', prof_resp.data)

        db.session.refresh(provisioned_user)
        self.assertFalse(provisioned_user.must_change_password)
        self.assertEqual(provisioned_user.email, 'lab.assistant@college.edu')
        self.assertEqual(fac2.email, 'lab.assistant@college.edu')

    def test_forgot_and_reset_password_via_otp(self):
        from unittest.mock import patch
        captured = {}

        def fake_send_otp(to_email, username, otp_code):
            captured['email'] = to_email
            captured['otp'] = otp_code
            return True, None

        with patch('app.auth.routes.send_otp_email', side_effect=fake_send_otp):
            resp = self.client.post('/auth/forgot-password', data={'identifier': 'testfaculty'}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(captured['email'], 'testfaculty@college.edu')
            self.assertEqual(len(captured['otp']), 6)

        # Wrong OTP increments attempts
        bad_resp = self.client.post('/auth/reset-password', data={
            'identifier': 'testfaculty',
            'otp': '000000',
            'new_password': 'ResetPass@123',
            'confirm_password': 'ResetPass@123',
        }, follow_redirects=True)
        self.assertIn(b'Invalid OTP code', bad_resp.data)

        # Valid OTP resets password
        ok_resp = self.client.post('/auth/reset-password', data={
            'identifier': 'testfaculty',
            'otp': captured['otp'],
            'new_password': 'ResetPass@123',
            'confirm_password': 'ResetPass@123',
        }, follow_redirects=True)
        self.assertEqual(ok_resp.status_code, 200)
        self.assertIn(b'Sign In', ok_resp.data)

        # Verify login works with new password
        login_resp = self.client.post('/auth/login', data={'username': 'testfaculty', 'password': 'ResetPass@123'}, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b'Sign Out', login_resp.data)


if __name__ == '__main__':
    unittest.main()
