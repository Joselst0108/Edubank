from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Institution, User, Loan

class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['name', 'primary_color', 'secondary_color', 'tertiary_color']
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'tertiary_color': forms.TextInput(attrs={'type': 'color'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']

class TransferForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.exclude(is_superuser=True),
        required=True,
        label="Recipient"
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    description = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        if self.sender:
            # Exclude the sender from the recipient list
            self.fields['recipient'].queryset = self.fields['recipient'].queryset.exclude(pk=self.sender.pk)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.sender.account.balance < amount:
            raise forms.ValidationError("You do not have sufficient funds for this transfer.")
        return amount

class LoanRequestForm(forms.ModelForm):
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.none(),
        required=True,
        label="Institution to request from"
    )

    class Meta:
        model = Loan
        fields = ['amount', 'institution']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filter institutions to those the user is a student at
            student_roles = user.roles.filter(role='student')
            institution_ids = student_roles.values_list('institution_id', flat=True)
            self.fields['institution'].queryset = Institution.objects.filter(id__in=institution_ids)

class StudentCreationForm(UserCreationForm):
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.none(),
        required=True,
        label="Institution"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Get all unique institution IDs from all of the user's roles
            institution_ids = user.roles.values_list('institution_id', flat=True).distinct()
            self.fields['institution'].queryset = Institution.objects.filter(id__in=institution_ids)

class LeadTeacherCreationForm(UserCreationForm):
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        required=True,
        label="Institution"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',)

class TeacherCreationForm(UserCreationForm):
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.none(),  # Start with an empty queryset
        required=True,
        label="Institution"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from the kwargs
        super().__init__(*args, **kwargs)
        if user:
            # Get the institutions where the user is a lead_teacher
            lead_teacher_roles = user.roles.filter(role='lead_teacher')
            institution_ids = lead_teacher_roles.values_list('institution_id', flat=True)
            self.fields['institution'].queryset = Institution.objects.filter(id__in=institution_ids)

class InstitutionUpdateForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['name', 'insignia', 'primary_color', 'secondary_color', 'tertiary_color']
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'tertiary_color': forms.TextInput(attrs={'type': 'color'}),
        }
