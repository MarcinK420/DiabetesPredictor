from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentBookingForm, AppointmentEditForm

@login_required
def patient_appointment_history(request):
    if not request.user.is_patient():
        return redirect('authentication:login')
    
    patient = request.user.patient_profile
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'appointments': page_obj,
        'patient': patient,
        'now': timezone.now(),
    }
    return render(request, 'appointments/patient_history.html', context)

@login_required
def appointment_detail(request, appointment_id):
    if not request.user.is_patient():
        return redirect('authentication:login')
    
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        patient=request.user.patient_profile
    )
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def book_appointment(request):
    """FR-06: Zapisywanie się na wizytę"""
    if not request.user.is_patient():
        messages.error(request, 'Tylko pacjenci mogą rezerwować wizyty.')
        return redirect('authentication:login')

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient_profile
            appointment.save()

            messages.success(request, 'Pomyślnie zapisano na wizytę!')
            return redirect('appointments:patient_history')
        else:
            messages.error(request, 'Sprawdź poprawność wprowadzonych danych.')
    else:
        form = AppointmentBookingForm()

    context = {
        'form': form,
        'title': 'Umów wizytę',
    }
    return render(request, 'appointments/book_appointment.html', context)


@login_required
def upcoming_appointments(request):
    """Wyświetla nadchodzące wizyty pacjenta"""
    if not request.user.is_patient():
        return redirect('authentication:login')

    patient = request.user.patient_profile
    appointments = Appointment.objects.filter(
        patient=patient,
        status='scheduled',
        appointment_date__gte=timezone.now()
    ).order_by('appointment_date')

    context = {
        'appointments': appointments,
        'patient': patient,
    }
    return render(request, 'appointments/upcoming_appointments.html', context)


@login_required
def edit_appointment(request, appointment_id):
    """FR-07: Edycja wizyty"""
    if not request.user.is_patient():
        messages.error(request, 'Tylko pacjenci mogą edytować swoje wizyty.')
        return redirect('authentication:login')

    # Get the appointment and ensure it belongs to the current patient
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user.patient_profile,
        status='scheduled'  # Only allow editing of scheduled appointments
    )

    # Check if appointment is in the future (can't edit past appointments)
    if appointment.appointment_date <= timezone.now():
        messages.error(request, 'Nie można edytować wizyty z przeszłości.')
        return redirect('appointments:upcoming')

    if request.method == 'POST':
        form = AppointmentEditForm(
            request.POST,
            instance=appointment,
            appointment_id=appointment.id
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Zapisano zmiany!')
            return redirect('appointments:upcoming')
        else:
            messages.error(request, 'Sprawdź poprawność wprowadzonych danych.')
    else:
        form = AppointmentEditForm(
            instance=appointment,
            appointment_id=appointment.id
        )

    context = {
        'form': form,
        'appointment': appointment,
        'title': 'Edytuj wizytę',
    }
    return render(request, 'appointments/edit_appointment.html', context)
