from django import forms
from django.core.exceptions import ValidationError
from appointments.models import Appointment, AppointmentAttachment
from ckeditor.widgets import CKEditorWidget


class AppointmentNotesForm(forms.ModelForm):
    """Formularz dla lekarza do edycji notatek z wizyty"""

    notes = forms.CharField(
        widget=CKEditorWidget(config_name='doctor_notes'),
        required=False,
        label='Notatki z wizyty',
        help_text='Wprowadź szczegółowe notatki z wizyty pacjenta'
    )

    status = forms.ChoiceField(
        choices=Appointment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status wizyty',
        help_text='Zaktualizuj status wizyty'
    )

    class Meta:
        model = Appointment
        fields = ['status', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        self.fields['status'].widget.attrs.update({'class': 'form-control'})


class AppointmentAttachmentForm(forms.ModelForm):
    """Formularz do przesyłania załączników do wizyty"""

    # Maksymalny rozmiar pliku: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    # Dozwolone rozszerzenia plików
    ALLOWED_EXTENSIONS = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Obrazy
        '.pdf', '.doc', '.docx', '.txt', '.rtf',  # Dokumenty
        '.xls', '.xlsx', '.csv',  # Arkusze
        '.zip', '.rar', '.7z'  # Archiwa
    ]

    file = forms.FileField(
        label='Plik',
        help_text='Maks. 10MB. Dozwolone: JPG, PNG, PDF, DOC, XLS, ZIP',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': ','.join(ALLOWED_EXTENSIONS)
        })
    )

    file_type = forms.ChoiceField(
        choices=AppointmentAttachment.FILE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Typ pliku',
        initial='other'
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Opcjonalny opis załącznika...'
        }),
        label='Opis'
    )

    class Meta:
        model = AppointmentAttachment
        fields = ['file', 'file_type', 'description']

    def clean_file(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file')

        if not file:
            return file

        # Check file size
        if file.size > self.MAX_FILE_SIZE:
            raise ValidationError(
                f'Plik jest za duży. Maksymalny rozmiar to {self.MAX_FILE_SIZE / (1024 * 1024):.0f}MB. '
                f'Twój plik ma {file.size / (1024 * 1024):.2f}MB.'
            )

        # Check file extension
        import os
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f'Niedozwolony typ pliku: {file_extension}. '
                f'Dozwolone rozszerzenia: {", ".join(self.ALLOWED_EXTENSIONS)}'
            )

        return file
