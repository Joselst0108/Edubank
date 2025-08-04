from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models

class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    insignia = models.ImageField(upload_to='insignias/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#00FF00')
    secondary_color = models.CharField(max_length=7, default='#FFFF00')
    tertiary_color = models.CharField(max_length=7, default='#FFFFFF')

    def __str__(self):
        return self.name

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

class UserRole(models.Model):
    STUDENT = 'student'
    TEACHER = 'teacher'
    LEAD_TEACHER = 'lead_teacher'
    ADMINISTRATOR = 'administrator'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (LEAD_TEACHER, 'Lead Teacher'),
        (ADMINISTRATOR, 'Administrator'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'role', 'institution')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} at {self.institution.name if self.institution else 'System'}"

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Account for {self.user.username}"

class Transaction(models.Model):
    sender_account = models.ForeignKey(Account, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient_account = models.ForeignKey(Account, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Transaction of {self.amount} from {self.sender_account.user.username} to {self.recipient_account.user.username}"

class Loan(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    student_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    request_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_loans')
    processed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Loan request for {self.student_account.user.username} of {self.amount:.2f}"
