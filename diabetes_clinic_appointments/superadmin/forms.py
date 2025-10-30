from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from authentication.models import User
from doctors.models import Doctor


class CreateDoctorForm(forms.Form):
    """Formularz do tworzenia konta lekarza przez superadmina"""

    # Dane logowania
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nazwa użytkownika'
        }),
        label='Nazwa użytkownika',
        help_text='Unikalny login lekarza do systemu'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hasło'
        }),
        label='Hasło',
        help_text='Minimum 8 znaków'
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Potwierdź hasło'
        }),
        label='Potwierdź hasło'
    )

    # Dane osobowe
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

    # Dane zawodowe - podstawowe (wymagane)
    license_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numer prawa wykonywania zawodu'
        }),
        label='Numer licencji',
        help_text='Unikalny numer prawa wykonywania zawodu'
    )

    specialization = forms.ChoiceField(
        choices=Doctor._meta.get_field('specialization').choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Specjalizacja'
    )

    years_of_experience = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Liczba lat'
        }),
        label='Lata doświadczenia'
    )

    consultation_fee = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        label='Cena konsultacji (zł)'
    )

    office_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Adres gabinetu...'
        }),
        label='Adres gabinetu'
    )

    working_hours_start = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        label='Godzina rozpoczęcia pracy'
    )

    working_hours_end = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        label='Godzina zakończenia pracy'
    )

    working_days = forms.ChoiceField(
        choices=Doctor._meta.get_field('working_days').choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Dni pracy'
    )

    education = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Wykształcenie, ukończone uczelnie, tytuły naukowe...'
        }),
        label='Wykształcenie'
    )

    is_accepting_patients = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Przyjmuje nowych pacjentów'
    )

    def clean_username(self):
        """Sprawdź czy nazwa użytkownika jest unikalna"""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Użytkownik o tej nazwie już istnieje.')
        return username

    def clean_email(self):
        """Sprawdź czy email jest unikalny"""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Użytkownik z tym adresem email już istnieje.')
        return email

    def clean_license_number(self):
        """Sprawdź czy numer licencji jest unikalny"""
        license_number = self.cleaned_data['license_number']
        if Doctor.objects.filter(license_number=license_number).exists():
            raise ValidationError('Lekarz o tym numerze licencji już istnieje.')
        return license_number

    def clean_password(self):
        """Waliduj hasło"""
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        """Sprawdź czy hasła się zgadzają"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Hasła nie są identyczne.')

        return cleaned_data

    def save(self):
        """Utwórz użytkownika i profil lekarza"""
        # Utwórz użytkownika
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone_number=self.cleaned_data.get('phone_number', ''),
            user_type='doctor'
        )

        # Utwórz profil lekarza
        doctor = Doctor.objects.create(
            user=user,
            license_number=self.cleaned_data['license_number'],
            specialization=self.cleaned_data['specialization'],
            years_of_experience=self.cleaned_data['years_of_experience'],
            office_address=self.cleaned_data['office_address'],
            consultation_fee=self.cleaned_data['consultation_fee'],
            working_hours_start=self.cleaned_data['working_hours_start'],
            working_hours_end=self.cleaned_data['working_hours_end'],
            working_days=self.cleaned_data['working_days'],
            education=self.cleaned_data['education'],
            certifications='',  # Lekarz uzupełni sam
            bio='',  # Lekarz uzupełni sam
            is_accepting_patients=self.cleaned_data['is_accepting_patients']
        )

        return user, doctor
