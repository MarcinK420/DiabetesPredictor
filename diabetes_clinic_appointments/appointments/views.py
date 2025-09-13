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

    # Check if patient can book appointment (2-minute cooldown after cancellation)
    patient = request.user.patient_profile
    if not patient.can_book_appointment():
        remaining_time = patient.time_until_can_book()
        seconds = int(remaining_time.total_seconds())
        minutes = seconds // 60
        seconds = seconds % 60
        messages.error(
            request,
            f'Musisz odczekać {minutes} minut i {seconds} sekund po anulowaniu wizyty przed zapisaniem się na nową.'
        )
        return redirect('appointments:upcoming')

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

    # Check cooldown status for template display
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
            'remaining_time': remaining_time
        }

    context = {
        'form': form,
        'title': 'Umów wizytę',
        'cooldown_info': cooldown_info,
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


@login_required
def cancel_appointment(request, appointment_id):
    """FR-08: Anulowanie wizyty"""
    if not request.user.is_patient():
        messages.error(request, 'Tylko pacjenci mogą anulować swoje wizyty.')
        return redirect('authentication:login')

    # Get the appointment and ensure it belongs to the current patient
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user.patient_profile,
        status='scheduled'  # Only allow cancellation of scheduled appointments
    )

    # Check if appointment is in the future (can't cancel past appointments)
    if appointment.appointment_date <= timezone.now():
        messages.error(request, 'Nie można anulować wizyty z przeszłości.')
        return redirect('appointments:upcoming')

    if request.method == 'POST':
        # Get confirmation from the form
        if request.POST.get('confirm_cancellation') == 'yes':
            # Cancel the appointment
            appointment.status = 'cancelled'
            appointment.save()

            # Update patient's last cancellation time
            patient = request.user.patient_profile
            patient.last_cancellation_time = timezone.now()
            patient.save()

            messages.success(request, 'Pomyślnie odwołano wizytę!')
            return redirect('appointments:upcoming')
        else:
            # User chose "No" - redirect back
            messages.info(request, 'Anulowanie zostało przerwane.')
            return redirect('appointments:upcoming')

    # GET request - show confirmation page
    context = {
        'appointment': appointment,
        'title': 'Anuluj wizytę',
    }
    return render(request, 'appointments/cancel_appointment.html', context)
