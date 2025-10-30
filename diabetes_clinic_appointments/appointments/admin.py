from django.contrib import admin
from .models import Appointment, AppointmentAttachment, NoteTemplate

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
