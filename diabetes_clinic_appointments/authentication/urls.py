from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_choice, name='register_choice'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
]