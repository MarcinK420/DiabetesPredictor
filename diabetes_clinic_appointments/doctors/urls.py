from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upcoming/', views.upcoming_appointments, name='upcoming_appointments'),
    path('patients/', views.patients_list, name='patients_list'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('appointment/<int:appointment_id>/notes/', views.edit_appointment_notes, name='edit_appointment_notes'),
    path('appointment/<int:appointment_id>/notes/view/', views.view_appointment_notes, name='view_appointment_notes'),
]