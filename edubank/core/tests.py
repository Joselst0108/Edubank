from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Institution, User, UserRole, Account, Loan, Transaction

class ModelTests(TestCase):

    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.institution = Institution.objects.create(name="Test School")
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.account = Account.objects.create(user=self.user, balance=Decimal('100.00'))

    def test_institution_creation(self):
        """Test that an institution can be created."""
        self.assertEqual(self.institution.name, "Test School")
        self.assertEqual(str(self.institution), "Test School")

    def test_user_creation(self):
        """Test that a user can be created."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('password123'))
        self.assertEqual(str(self.user), 'testuser')

    def test_user_role_creation(self):
        """Test creating a user role."""
        role = UserRole.objects.create(
            user=self.user,
            role='student',
            institution=self.institution
        )
        self.assertEqual(role.user, self.user)
        self.assertEqual(role.role, 'student')
        self.assertEqual(role.institution, self.institution)
        self.assertEqual(
            str(role),
            "testuser - Student at Test School"
        )

    def test_account_creation(self):
        """Test account properties."""
        self.assertEqual(self.account.user, self.user)
        self.assertEqual(self.account.balance, Decimal('100.00'))
        self.assertEqual(str(self.account), "Account for testuser")

    def test_loan_creation(self):
        """Test that a loan is created with a pending status."""
        loan = Loan.objects.create(
            student_account=self.account,
            institution=self.institution,
            amount=Decimal('50.00')
        )
        self.assertEqual(loan.student_account, self.account)
        self.assertEqual(loan.amount, Decimal('50.00'))
        self.assertEqual(loan.status, Loan.PENDING)
        self.assertEqual(
            str(loan),
            "Loan request for testuser of 50.00"
        )

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Institutions
        self.inst_a = Institution.objects.create(name="Hogwarts")
        self.inst_b = Institution.objects.create(name="Beauxbatons")

        # Users
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.lead_teacher = User.objects.create_user('leadteacher', 'lt@test.com', 'password')
        self.teacher_a = User.objects.create_user('teacher_a', 'ta@test.com', 'password')
        self.teacher_b = User.objects.create_user('teacher_b', 'tb@test.com', 'password')
        self.student = User.objects.create_user('student', 'student@test.com', 'password')

        # Accounts
        Account.objects.create(user=self.admin_user)
        Account.objects.create(user=self.lead_teacher)
        Account.objects.create(user=self.teacher_a)
        Account.objects.create(user=self.teacher_b)
        self.student_account = Account.objects.create(user=self.student, balance=Decimal('100.00'))

        # Roles
        UserRole.objects.create(user=self.admin_user, role='administrator')
        UserRole.objects.create(user=self.lead_teacher, role='lead_teacher', institution=self.inst_a)
        UserRole.objects.create(user=self.teacher_a, role='teacher', institution=self.inst_a)
        UserRole.objects.create(user=self.teacher_b, role='teacher', institution=self.inst_b)
        UserRole.objects.create(user=self.student, role='student', institution=self.inst_a)

    def test_permissions_unauthenticated(self):
        """Test that unauthenticated users are redirected from protected views."""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')

    def test_permissions_admin_view(self):
        """Test that only admins can access admin views."""
        self.client.login(username='teacher_a', password='password')
        response = self.client.get(reverse('core:create_institution'))
        self.assertEqual(response.status_code, 403) # PermissionDenied

        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('core:create_institution'))
        self.assertEqual(response.status_code, 200)

    def test_approve_loan_view(self):
        """Test the logic for approving a loan."""
        loan = Loan.objects.create(
            student_account=self.student_account,
            institution=self.inst_a,
            amount=Decimal('50.00')
        )

        # Login as the correct teacher
        self.client.login(username='teacher_a', password='password')

        initial_balance = self.student_account.balance

        response = self.client.post(reverse('core:approve_loan', args=[loan.id]))

        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:loan_request_list'))

        # Refresh objects from DB
        loan.refresh_from_db()
        self.student_account.refresh_from_db()

        # Check loan status
        self.assertEqual(loan.status, 'approved')
        self.assertEqual(loan.processed_by, self.teacher_a)

        # Check balance update
        self.assertEqual(self.student_account.balance, initial_balance + loan.amount)

    def test_approve_loan_permission_denied(self):
        """Test that a teacher from another institution cannot approve a loan."""
        loan = Loan.objects.create(
            student_account=self.student_account,
            institution=self.inst_a,
            amount=Decimal('50.00')
        )

        # Login as teacher from institution B
        self.client.login(username='teacher_b', password='password')

        response = self.client.post(reverse('core:approve_loan', args=[loan.id]))
        self.assertEqual(response.status_code, 403) # PermissionDenied

    def test_student_request_loan_view(self):
        """Test that a student can request a loan."""
        self.client.login(username='student', password='password')

        loan_count_before = Loan.objects.count()

        response = self.client.post(reverse('core:request_loan'), {
            'amount': '25.50',
            'institution': self.inst_a.id
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))
        self.assertEqual(Loan.objects.count(), loan_count_before + 1)

        new_loan = Loan.objects.latest('request_date')
        self.assertEqual(new_loan.student_account, self.student_account)
        self.assertEqual(new_loan.amount, Decimal('25.50'))
        self.assertEqual(new_loan.status, 'pending')

    def test_student_transfer_money_view(self):
        """Test a successful money transfer."""
        # Note: self.teacher_a is the recipient in this test
        self.client.login(username='student', password='password')

        sender_initial_balance = self.student_account.balance
        recipient_initial_balance = self.teacher_a.account.balance

        response = self.client.post(reverse('core:transfer_money'), {
            'recipient': self.teacher_a.id,
            'amount': '10.00',
            'description': 'Test transfer'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))

        self.student_account.refresh_from_db()
        self.teacher_a.account.refresh_from_db()

        self.assertEqual(self.student_account.balance, sender_initial_balance - Decimal('10.00'))
        self.assertEqual(self.teacher_a.account.balance, recipient_initial_balance + Decimal('10.00'))

        self.assertTrue(Transaction.objects.filter(description='Test transfer').exists())

    def test_student_transfer_insufficient_funds(self):
        """Test that a transfer fails with insufficient funds."""
        self.client.login(username='student', password='password')

        response = self.client.post(reverse('core:transfer_money'), {
            'recipient': self.teacher_a.id,
            'amount': '1000.00', # More than the student has
        })

        # The view should re-render the form with an error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You do not have sufficient funds")
