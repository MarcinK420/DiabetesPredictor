from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PatientProfileForm

@login_required
def dashboard(request):
    if not request.user.is_patient():
        return redirect('authentication:login')

    # Check cooldown status for appointment booking button
    patient = request.user.patient_profile
    cooldown_info = None
    if not patient.can_book_appointment():
        remaining_time = patient.time_until_can_book()
        seconds = int(remaining_time.total_seconds())
        minutes = seconds // 60
        seconds = seconds % 60
        cooldown_info = {
            'active': True,
            'minutes': minutes,
            'seconds': seconds,
        }

    context = {
        'cooldown_info': cooldown_info,
    }

    return render(request, 'patients/dashboard.html', context)


@login_required
def profile(request):
    """FR-09: Karta z danymi pacjenta"""
    if not request.user.is_patient():
        return redirect('authentication:login')

    patient = request.user.patient_profile

    # Get appointment statistics
    last_appointment = patient.get_last_appointment()
    next_appointment = patient.get_next_appointment()
    total_appointments = patient.get_total_appointments()

    context = {
        'patient': patient,
        'last_appointment': last_appointment,
        'next_appointment': next_appointment,
        'total_appointments': total_appointments,
        'age': patient.get_age(),
    }

    return render(request, 'patients/profile.html', context)


@login_required
def edit_profile(request):
    """FR-09: Edycja profilu pacjenta"""
    if not request.user.is_patient():
        return redirect('authentication:login')

    patient = request.user.patient_profile

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil został pomyślnie zaktualizowany!')
            return redirect('patients:profile')
        else:
            messages.error(request, 'Sprawdź poprawność wprowadzonych danych.')
    else:
        form = PatientProfileForm(instance=patient, user=request.user)

    context = {
        'form': form,
        'patient': patient,
    }

    return render(request, 'patients/edit_profile.html', context)
