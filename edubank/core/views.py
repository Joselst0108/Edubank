from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from .decorators import role_required
from .forms import InstitutionForm, LeadTeacherCreationForm, TeacherCreationForm, InstitutionUpdateForm, StudentCreationForm, LoanRequestForm, TransferForm, ProfileUpdateForm
from .models import Account, UserRole, Institution, Loan, Transaction

def home(request):
    """
    Renders the main landing page for the application.
    This page will contain general information about edubank and a login form.
    """
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    """
    This view acts as the main hub for a logged-in user.
    It retrieves all roles associated with the user (e.g., student, teacher)
    and their corresponding institutions, then passes this information to the dashboard template.
    """
    # Eagerly fetch related institution data to avoid extra database queries in the template
    user_roles = request.user.roles.select_related('institution').all()
    role_names = [role.role for role in user_roles]

    context = {
        'user_roles': user_roles,
        'role_names': role_names,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@role_required(['administrator'])
def create_institution(request):
    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard')
    else:
        form = InstitutionForm()
    return render(request, 'core/create_institution.html', {'form': form, 'title': 'Create New Institution'})

@login_required
@role_required(['administrator'])
def create_lead_teacher(request):
    if request.method == 'POST':
        form = LeadTeacherCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create an account for the new user
            Account.objects.create(user=user)
            # Assign the role
            institution = form.cleaned_data['institution']
            UserRole.objects.create(user=user, role='lead_teacher', institution=institution)
            return redirect('core:dashboard')
    else:
        form = LeadTeacherCreationForm()
    return render(request, 'core/create_user.html', {'form': form, 'title': 'Create New Lead Teacher'})

@login_required
@role_required(['lead_teacher'])
def create_teacher(request):
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user)
            institution = form.cleaned_data['institution']
            UserRole.objects.create(user=user, role='teacher', institution=institution)
            return redirect('core:dashboard')
    else:
        form = TeacherCreationForm(user=request.user)
    return render(request, 'core/create_user.html', {'form': form, 'title': 'Create New Teacher'})

@login_required
@role_required(['lead_teacher'])
def update_institution(request, institution_id):
    institution = get_object_or_404(Institution, pk=institution_id)

    # Security check: Ensure the user is a lead teacher for this specific institution
    is_lead_teacher_for_institution = request.user.roles.filter(
        role='lead_teacher',
        institution=institution
    ).exists()

    if not is_lead_teacher_for_institution and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = InstitutionUpdateForm(request.POST, request.FILES, instance=institution)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard')
    else:
        form = InstitutionUpdateForm(instance=institution)

    return render(request, 'core/update_institution.html', {'form': form, 'institution': institution, 'title': f'Update {institution.name}'})

@login_required
@role_required(['teacher', 'lead_teacher'])
def create_student(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user)
            institution = form.cleaned_data['institution']
            UserRole.objects.create(user=user, role='student', institution=institution)
            return redirect('core:dashboard')
    else:
        form = StudentCreationForm(user=request.user)
    return render(request, 'core/create_user.html', {'form': form, 'title': 'Create New Student'})

@login_required
@role_required(['teacher', 'lead_teacher'])
def loan_request_list(request):
    # Get the institutions the user is a teacher or lead_teacher at
    teacher_institutions = Institution.objects.filter(
        userrole__user=request.user,
        userrole__role__in=['teacher', 'lead_teacher']
    ).distinct()

    # Get all pending loans from those institutions
    pending_loans = Loan.objects.filter(
        institution__in=teacher_institutions,
        status=Loan.PENDING
    ).select_related('student_account__user', 'institution')

    context = {
        'pending_loans': pending_loans,
        'title': 'Pending Loan Requests'
    }
    return render(request, 'core/loan_request_list.html', context)

@require_POST
@login_required
@role_required(['teacher', 'lead_teacher'])
def approve_loan(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id, status=Loan.PENDING)

    # Security check
    teacher_institutions = Institution.objects.filter(
        userrole__user=request.user,
        userrole__role__in=['teacher', 'lead_teacher']
    ).distinct()
    if loan.institution not in teacher_institutions and not request.user.is_superuser:
        raise PermissionDenied

    with transaction.atomic():
        # Update student's account balance
        student_account = loan.student_account
        student_account.balance += loan.amount
        student_account.save()

        # Update loan status
        loan.status = Loan.APPROVED
        loan.processed_by = request.user
        loan.processed_date = timezone.now()
        loan.save()

    return redirect('core:loan_request_list')

@require_POST
@login_required
@role_required(['teacher', 'lead_teacher'])
def deny_loan(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id, status=Loan.PENDING)

    # Security check
    teacher_institutions = Institution.objects.filter(
        userrole__user=request.user,
        userrole__role__in=['teacher', 'lead_teacher']
    ).distinct()
    if loan.institution not in teacher_institutions and not request.user.is_superuser:
        raise PermissionDenied

    loan.status = Loan.REJECTED
    loan.processed_by = request.user
    loan.processed_date = timezone.now()
    loan.save()

    return redirect('core:loan_request_list')

@login_required
@role_required(['student'])
def request_loan(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST, user=request.user)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.student_account = request.user.account
            loan.save()
            return redirect('core:dashboard')
    else:
        form = LoanRequestForm(user=request.user)

    return render(request, 'core/request_loan.html', {'form': form, 'title': 'Request a Loan'})

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'core/update_profile.html', {'form': form, 'title': 'Update Profile'})

@login_required
@role_required(['student'])
def transfer_money(request):
    if request.method == 'POST':
        form = TransferForm(request.POST, sender=request.user)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            sender_account = request.user.account
            recipient_account = recipient.account

            try:
                with transaction.atomic():
                    sender_account.balance -= amount
                    sender_account.save()

                    recipient_account.balance += amount
                    recipient_account.save()

                    Transaction.objects.create(
                        sender_account=sender_account,
                        recipient_account=recipient_account,
                        amount=amount,
                        description=description
                    )
                # Add a success message here if you have messages framework
                return redirect('core:dashboard')
            except Exception as e:
                # Handle potential errors during transaction
                form.add_error(None, f"An unexpected error occurred: {e}")

    else:
        form = TransferForm(sender=request.user)

    return render(request, 'core/transfer_money.html', {'form': form, 'title': 'Transfer Money'})
