from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('history/', views.patient_appointment_history, name='patient_history'),
    path('detail/<int:appointment_id>/', views.appointment_detail, name='detail'),
]