from django import forms
from django.core.exceptions import ValidationError
from appointments.models import Appointment, AppointmentAttachment, NoteTemplate
from doctors.models import Doctor
from authentication.models import User
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


class NoteTemplateForm(forms.ModelForm):
    """Formularz do zarządzania szablonami notatek"""

    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Np. Konsultacja diabetologiczna - nowy pacjent'
        }),
        label='Nazwa szablonu',
        help_text='Podaj opisową nazwę szablonu'
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Krótki opis przeznaczenia szablonu...'
        }),
        label='Opis',
        help_text='Opcjonalny opis, kiedy stosować ten szablon'
    )

    content = forms.CharField(
        widget=CKEditorWidget(config_name='doctor_notes'),
        label='Treść szablonu',
        help_text='Wprowadź treść szablonu z formatowaniem'
    )

    category = forms.ChoiceField(
        choices=NoteTemplate.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Kategoria'
    )

    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Szablon aktywny',
        help_text='Czy szablon jest dostępny do użycia'
    )

    class Meta:
        model = NoteTemplate
        fields = ['name', 'description', 'content', 'category', 'is_active']


class DoctorProfileForm(forms.ModelForm):
    """Formularz do edycji profilu lekarza"""

    # Pola z modelu User
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Imię'
        }),
        label='Imię'
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nazwisko'
        }),
        label='Nazwisko'
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        label='Email'
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+48 123 456 789'
        }),
        label='Numer telefonu'
    )

    class Meta:
        model = Doctor
        fields = [
            'specialization', 'years_of_experience', 'office_address',
            'consultation_fee', 'working_hours_start', 'working_hours_end',
            'working_days', 'education', 'certifications', 'bio',
            'is_accepting_patients'
        ]
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Liczba lat'
            }),
            'office_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adres gabinetu...'
            }),
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'working_hours_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'working_hours_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'working_days': forms.Select(attrs={'class': 'form-control'}),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Wykształcenie, uczelnie, tytuły naukowe...'
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Certyfikaty, kursy, specjalizacje...'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Krótki opis o sobie, zainteresowania zawodowe...'
            }),
            'is_accepting_patients': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'specialization': 'Specjalizacja',
            'years_of_experience': 'Lata doświadczenia',
            'office_address': 'Adres gabinetu',
            'consultation_fee': 'Cena konsultacji (zł)',
            'working_hours_start': 'Godzina rozpoczęcia pracy',
            'working_hours_end': 'Godzina zakończenia pracy',
            'working_days': 'Dni pracy',
            'education': 'Wykształcenie',
            'certifications': 'Certyfikaty',
            'bio': 'Biografia',
            'is_accepting_patients': 'Przyjmuję nowych pacjentów',
        }

    def __init__(self, *args, **kwargs):
        # Extract user instance if provided
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Populate user fields if user is provided
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['phone_number'].initial = self.user.phone_number

    def save(self, commit=True):
        """Save both Doctor and User instances"""
        doctor = super().save(commit=False)

        # Update user fields
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.phone_number = self.cleaned_data['phone_number']

            if commit:
                self.user.save()

        if commit:
            doctor.save()

        return doctor
