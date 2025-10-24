from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('history/', views.patient_appointment_history, name='patient_history'),
    path('detail/<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('upcoming/', views.upcoming_appointments, name='upcoming'),
    path('edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('api/available-slots/', views.get_available_time_slots, name='available_time_slots'),
]