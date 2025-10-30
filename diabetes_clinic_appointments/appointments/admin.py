from django.contrib import admin
from .models import Appointment, AppointmentAttachment, NoteTemplate, DiabetesPrediction

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status', 'reason']
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'reason']
    ordering = ['-appointment_date']
    date_hierarchy = 'appointment_date'


@admin.register(AppointmentAttachment)
class AppointmentAttachmentAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'file_type', 'filename', 'file_size_mb', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at', 'uploaded_by']
    search_fields = ['appointment__patient__user__first_name', 'appointment__patient__user__last_name', 'description']
    ordering = ['-uploaded_at']
    readonly_fields = ['file_size', 'uploaded_at']
    date_hierarchy = 'uploaded_at'

    def filename(self, obj):
        return obj.filename
    filename.short_description = 'Nazwa pliku'


@admin.register(NoteTemplate)
class NoteTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_by', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'content']
    ordering = ['category', 'name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Treść szablonu', {
            'fields': ('content',)
        }),
        ('Metadane', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DiabetesPrediction)
class DiabetesPredictionAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'get_patient', 'get_doctor', 'risk_level', 'percentage', 'created_at']
    list_filter = ['risk_level', 'created_at', 'created_by']
    search_fields = [
        'appointment__patient__user__first_name',
        'appointment__patient__user__last_name',
        'appointment__doctor__user__first_name',
        'appointment__doctor__user__last_name'
    ]
    ordering = ['-created_at']
    readonly_fields = ['probability', 'percentage', 'risk_level', 'risk_color', 'created_at', 'created_by']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Wizyta', {
            'fields': ('appointment',)
        }),
        ('Dane wejściowe', {
            'fields': ('pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
                      'insulin', 'bmi', 'diabetes_pedigree', 'age')
        }),
        ('Wyniki predykcji', {
            'fields': ('probability', 'percentage', 'risk_level', 'risk_color'),
            'classes': ('collapse',)
        }),
        ('Metadane', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_patient(self, obj):
        return f"{obj.appointment.patient.user.first_name} {obj.appointment.patient.user.last_name}"
    get_patient.short_description = 'Pacjent'
    get_patient.admin_order_field = 'appointment__patient__user__last_name'

    def get_doctor(self, obj):
        return f"Dr. {obj.appointment.doctor.user.last_name}"
    get_doctor.short_description = 'Lekarz'
    get_doctor.admin_order_field = 'appointment__doctor__user__last_name'

    def percentage(self, obj):
        return f"{obj.percentage:.1f}%"
    percentage.short_description = 'Ryzyko (%)'
