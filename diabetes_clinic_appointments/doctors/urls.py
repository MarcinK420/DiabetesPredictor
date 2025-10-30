from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.doctor_profile, name='doctor_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('upcoming/', views.upcoming_appointments, name='upcoming_appointments'),
    path('patients/', views.patients_list, name='patients_list'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('appointment/<int:appointment_id>/notes/', views.edit_appointment_notes, name='edit_appointment_notes'),
    path('appointment/<int:appointment_id>/notes/view/', views.view_appointment_notes, name='view_appointment_notes'),
    path('attachment/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    path('attachment/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
    # Note Templates
    path('templates/', views.list_templates, name='list_templates'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/<int:template_id>/edit/', views.edit_template, name='edit_template'),
    path('templates/<int:template_id>/delete/', views.delete_template, name='delete_template'),
    path('templates/<int:template_id>/content/', views.get_template_content, name='get_template_content'),
    # Diabetes Risk Assessment
    path('appointment/<int:appointment_id>/diabetes-risk/', views.diabetes_risk_assessment, name='diabetes_risk_assessment'),
]