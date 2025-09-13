from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'years_of_experience', 'is_accepting_patients', 'created_at']
    list_filter = ['specialization', 'is_accepting_patients', 'working_days', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'license_number']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('user', 'license_number', 'specialization', 'years_of_experience')
        }),
        ('Gabinet i godziny pracy', {
            'fields': ('office_address', 'consultation_fee', 'working_hours_start', 'working_hours_end', 'working_days')
        }),
        ('Wykształcenie i doświadczenie', {
            'fields': ('education', 'certifications', 'bio')
        }),
        ('Status', {
            'fields': ('is_accepting_patients',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields
