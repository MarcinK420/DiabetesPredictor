from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status', 'reason']
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'reason']
    ordering = ['-appointment_date']
    date_hierarchy = 'appointment_date'
