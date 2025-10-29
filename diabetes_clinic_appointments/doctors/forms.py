from django import forms
from appointments.models import Appointment
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
