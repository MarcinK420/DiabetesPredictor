from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor
from ckeditor.fields import RichTextField
import os


def appointment_attachment_path(instance, filename):
    """Generate upload path for appointment attachments"""
    # Format: appointments/patient_ID/appointment_ID/filename
    return f'appointments/patient_{instance.appointment.patient.id}/appointment_{instance.appointment.id}/{filename}'

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Zaplanowana'),
        ('completed', 'Zakończona'),
        ('cancelled', 'Anulowana'),
        ('no_show', 'Niestawiennictwo'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'Brak powtórzeń'),
        ('weekly', 'Co tydzień'),
        ('biweekly', 'Co 2 tygodnie'),
        ('monthly', 'Co miesiąc'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    reason = models.CharField(max_length=200, help_text="Powód wizyty")
    notes = RichTextField(blank=True, null=True, config_name='doctor_notes', help_text="Notatki z wizyty (dla lekarza)")
    duration_minutes = models.PositiveIntegerField(default=30)

    # Recurring appointment fields
    is_recurring = models.BooleanField(default=False, help_text="Czy wizyta jest częścią serii")
    recurrence_pattern = models.CharField(
        max_length=15,
        choices=RECURRENCE_CHOICES,
        default='none',
        help_text="Wzorzec powtarzania"
    )
    recurrence_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Data końca powtarzania serii"
    )
    parent_appointment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recurring_instances',
        help_text="Pierwsza wizyta w serii (dla śledzenia całej serii)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date']
        verbose_name = "Wizyta"
        verbose_name_plural = "Wizyty"

    def __str__(self):
        return f"{self.patient.user.first_name} {self.patient.user.last_name} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')} - Dr. {self.doctor.user.last_name}"

    def get_series_appointments(self):
        """Zwraca wszystkie wizyty w serii (włączając tę wizytę)"""
        if self.parent_appointment:
            # To jest jedna z wizyt w serii, zwróć wszystkie z tej samej serii
            return Appointment.objects.filter(
                models.Q(parent_appointment=self.parent_appointment) |
                models.Q(id=self.parent_appointment.id)
            ).order_by('appointment_date')
        elif self.is_recurring:
            # To jest pierwsza wizyta w serii, zwróć ją i wszystkie jej instancje
            return Appointment.objects.filter(
                models.Q(parent_appointment=self) |
                models.Q(id=self.id)
            ).order_by('appointment_date')
        else:
            # To jest pojedyncza wizyta
            return Appointment.objects.filter(id=self.id)


class AppointmentAttachment(models.Model):
    """Model for storing attachments (images, documents, test results) for appointments"""

    FILE_TYPE_CHOICES = [
        ('image', 'Zdjęcie'),
        ('document', 'Dokument'),
        ('test_result', 'Wynik badania'),
        ('other', 'Inne'),
    ]

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Wizyta'
    )
    file = models.FileField(
        upload_to=appointment_attachment_path,
        verbose_name='Plik'
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='other',
        verbose_name='Typ pliku'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Opis',
        help_text='Opcjonalny opis załącznika'
    )
    uploaded_by = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Dodane przez'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data uploadu'
    )
    file_size = models.IntegerField(
        default=0,
        verbose_name='Rozmiar pliku (bajty)'
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Załącznik do wizyty"
        verbose_name_plural = "Załączniki do wizyt"

    def __str__(self):
        return f"{self.get_file_type_display()} - {self.file.name}"

    def save(self, *args, **kwargs):
        """Override save to store file size"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def filename(self):
        """Return just the filename without path"""
        return os.path.basename(self.file.name)

    @property
    def file_extension(self):
        """Return file extension"""
        return os.path.splitext(self.file.name)[1].lower()

    @property
    def is_image(self):
        """Check if file is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
        return self.file_extension in image_extensions

    @property
    def is_pdf(self):
        """Check if file is a PDF"""
        return self.file_extension == '.pdf'

    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class NoteTemplate(models.Model):
    """Model for storing reusable note templates for common cases"""

    CATEGORY_CHOICES = [
        ('consultation', 'Konsultacja'),
        ('checkup', 'Kontrola'),
        ('test_results', 'Wyniki badań'),
        ('medication', 'Zmiana leczenia'),
        ('diet', 'Dieta'),
        ('complication', 'Powikłanie'),
        ('education', 'Edukacja pacjenta'),
        ('other', 'Inne'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name='Nazwa szablonu',
        help_text='Nazwa szablonu wyświetlana na liście'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Opis',
        help_text='Krótki opis przeznaczenia szablonu'
    )
    content = RichTextField(
        config_name='doctor_notes',
        verbose_name='Treść szablonu',
        help_text='Treść szablonu notatki (HTML)'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Kategoria'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Aktywny',
        help_text='Czy szablon jest dostępny do użycia'
    )
    created_by = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Utworzony przez',
        related_name='created_templates'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data utworzenia'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Data aktualizacji'
    )

    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Szablon notatki"
        verbose_name_plural = "Szablony notatek"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
