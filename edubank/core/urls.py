from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('institutions/create/', views.create_institution, name='create_institution'),
    path('users/create/lead-teacher/', views.create_lead_teacher, name='create_lead_teacher'),
    path('users/create/teacher/', views.create_teacher, name='create_teacher'),
    path('institutions/<int:institution_id>/update/', views.update_institution, name='update_institution'),
    path('users/create/student/', views.create_student, name='create_student'),
    path('loans/pending/', views.loan_request_list, name='loan_request_list'),
    path('loans/<int:loan_id>/approve/', views.approve_loan, name='approve_loan'),
    path('loans/<int:loan_id>/deny/', views.deny_loan, name='deny_loan'),
    path('loans/request/', views.request_loan, name='request_loan'),
    path('transfer/', views.transfer_money, name='transfer_money'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
