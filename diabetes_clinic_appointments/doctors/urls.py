from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upcoming/', views.upcoming_appointments, name='upcoming_appointments'),
]