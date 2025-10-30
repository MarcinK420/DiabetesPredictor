from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('doctors/create/', views.create_doctor, name='create_doctor'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/unlock/', views.unlock_user_account, name='unlock_user_account'),
    path('users/<int:user_id>/lock/', views.lock_user_account, name='lock_user_account'),
    path('users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
    path('users/<int:user_id>/toggle-superuser/', views.toggle_superuser_status, name='toggle_superuser_status'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
]
