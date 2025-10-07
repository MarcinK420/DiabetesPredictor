from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from patients.models import Patient
from doctors.models import Doctor

class PatientRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    first_name = forms.CharField(max_length=30, required=True, label='Imię')
    last_name = forms.CharField(max_length=30, required=True, label='Nazwisko')
    email = forms.EmailField(required=True, label='Email')
    phone_number = forms.CharField(max_length=15, required=False, label='Numer telefonu')
    
    date_of_birth = forms.DateField(required=True, label='Data urodzenia', widget=forms.DateInput(attrs={'type': 'date'}))
    pesel = forms.CharField(max_length=11, required=True, label='PESEL')
    address = forms.CharField(widget=forms.Textarea, required=True, label='Adres')
    emergency_contact_name = forms.CharField(max_length=100, required=True, label='Kontakt awaryjny - imię')
    emergency_contact_phone = forms.CharField(max_length=15, required=True, label='Kontakt awaryjny - telefon')
    
    diabetes_type = forms.ChoiceField(
        choices=Patient._meta.get_field('diabetes_type').choices,
        required=True,
        label='Typ cukrzycy'
    )
    diagnosis_date = forms.DateField(required=False, label='Data diagnozy', widget=forms.DateInput(attrs={'type': 'date'}))
    current_medications = forms.CharField(widget=forms.Textarea, required=False, label='Aktualne leki')
    allergies = forms.CharField(widget=forms.Textarea, required=False, label='Alergie')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        diabetes_type = cleaned_data.get('diabetes_type')
        diagnosis_date = cleaned_data.get('diagnosis_date')

        if diabetes_type and diabetes_type != 'healthy' and not diagnosis_date:
            raise forms.ValidationError('Data diagnozy jest wymagana dla osób z cukrzycą.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'patient'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                pesel=self.cleaned_data['pesel'],
                address=self.cleaned_data['address'],
                emergency_contact_name=self.cleaned_data['emergency_contact_name'],
                emergency_contact_phone=self.cleaned_data['emergency_contact_phone'],
                diabetes_type=self.cleaned_data['diabetes_type'],
                diagnosis_date=self.cleaned_data.get('diagnosis_date'),
                current_medications=self.cleaned_data['current_medications'],
                allergies=self.cleaned_data['allergies'],
            )
        return user

class DoctorRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    first_name = forms.CharField(max_length=30, required=True, label='Imię')
    last_name = forms.CharField(max_length=30, required=True, label='Nazwisko')
    email = forms.EmailField(required=True, label='Email')
    phone_number = forms.CharField(max_length=15, required=False, label='Numer telefonu')
    
    license_number = forms.CharField(max_length=20, required=True, label='Numer licencji')
    specialization = forms.ChoiceField(
        choices=Doctor._meta.get_field('specialization').choices,
        required=True,
        label='Specjalizacja'
    )
    years_of_experience = forms.IntegerField(required=True, label='Lata doświadczenia')
    office_address = forms.CharField(widget=forms.Textarea, required=True, label='Adres gabinetu')
    consultation_fee = forms.DecimalField(max_digits=6, decimal_places=2, required=True, label='Opłata za konsultację')
    
    working_hours_start = forms.TimeField(required=True, label='Początek godzin pracy', widget=forms.TimeInput(attrs={'type': 'time'}))
    working_hours_end = forms.TimeField(required=True, label='Koniec godzin pracy', widget=forms.TimeInput(attrs={'type': 'time'}))
    working_days = forms.ChoiceField(
        choices=Doctor._meta.get_field('working_days').choices,
        required=True,
        label='Dni pracy'
    )
    
    education = forms.CharField(widget=forms.Textarea, required=True, label='Wykształcenie')
    certifications = forms.CharField(widget=forms.Textarea, required=False, label='Certyfikaty')
    bio = forms.CharField(widget=forms.Textarea, required=False, label='Biografia')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'doctor'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
            Doctor.objects.create(
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
                certifications=self.cleaned_data['certifications'],
                bio=self.cleaned_data['bio'],
            )
        return user