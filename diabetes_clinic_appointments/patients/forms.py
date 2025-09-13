from django import forms
from django.contrib.auth import get_user_model
from .models import Patient

User = get_user_model()


class PatientProfileForm(forms.ModelForm):
    """Formularz edycji profilu pacjenta (FR-09)"""

    # User fields
    first_name = forms.CharField(
        max_length=30,
        label='Imię',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=30,
        label='Nazwisko',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label='Telefon',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Patient fields
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Adres'
    )

    emergency_contact_name = forms.CharField(
        max_length=100,
        label='Osoba kontaktowa (awaryjnie)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    emergency_contact_phone = forms.CharField(
        max_length=15,
        label='Telefon awaryjny',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    current_medications = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Obecne leki',
        help_text='Lista aktualnie przyjmowanych leków'
    )

    allergies = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Alergie',
        help_text='Znane alergie i nietolerancje'
    )

    class Meta:
        model = Patient
        fields = ['address', 'emergency_contact_name', 'emergency_contact_phone',
                 'current_medications', 'allergies']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Pre-populate user fields
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['phone_number'].initial = self.user.phone_number

    def save(self, commit=True):
        # Save patient instance
        patient = super().save(commit=False)

        if self.user:
            # Update user fields
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.phone_number = self.cleaned_data['phone_number']

            if commit:
                self.user.save()

        if commit:
            patient.save()

        return patient