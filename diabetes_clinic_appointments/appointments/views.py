from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta, time
from .models import Appointment
from .forms import AppointmentBookingForm, AppointmentEditForm
from doctors.models import Doctor

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


@login_required
def get_available_time_slots(request):
    """
    API endpoint that returns available time slots for a specific doctor on a specific date.
    Returns JSON with available hours.
    """
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')  # Format: YYYY-MM-DD
    appointment_id = request.GET.get('appointment_id')  # Optional: for editing

    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    try:
        doctor = Doctor.objects.get(id=doctor_id)
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (Doctor.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid doctor or date'}, status=400)

    # Check if the date is a weekend
    if selected_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return JsonResponse({'available_slots': [], 'message': 'Weekends are not available'})

    # Generate all possible time slots (8:00 - 17:00, every 15 minutes)
    all_slots = []
    current_time = time(8, 0)  # Start at 8:00
    end_time = time(17, 0)     # End at 17:00

    while current_time < end_time:
        all_slots.append(current_time.strftime('%H:%M'))
        # Add 15 minutes
        dt = datetime.combine(selected_date, current_time)
        dt += timedelta(minutes=15)
        current_time = dt.time()

    # Get all scheduled appointments for this doctor on this date
    start_datetime = datetime.combine(selected_date, time(0, 0))
    end_datetime = datetime.combine(selected_date, time(23, 59))

    # Make datetimes timezone-aware
    start_datetime = timezone.make_aware(start_datetime)
    end_datetime = timezone.make_aware(end_datetime)

    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__range=(start_datetime, end_datetime),
        status='scheduled'
    )

    # Exclude current appointment if editing
    if appointment_id:
        existing_appointments = existing_appointments.exclude(id=appointment_id)

    # Mark occupied slots (including buffer time)
    occupied_slots = set()
    for appointment in existing_appointments:
        appointment_time = appointment.appointment_date.astimezone(timezone.get_current_timezone())

        # Block the exact time slot and 45 minutes after (30 min appointment + 15 min buffer)
        current = appointment_time
        for _ in range(4):  # 4 slots of 15 minutes = 60 minutes total
            occupied_slots.add(current.time().strftime('%H:%M'))
            current += timedelta(minutes=15)

        # Also block 15 minutes before
        before = appointment_time - timedelta(minutes=15)
        if before.time() >= time(8, 0):
            occupied_slots.add(before.time().strftime('%H:%M'))

    # Filter available slots
    available_slots = [slot for slot in all_slots if slot not in occupied_slots]

    return JsonResponse({
        'available_slots': available_slots,
        'occupied_slots': list(occupied_slots),
        'date': date_str,
        'doctor_name': f"Dr. {doctor.user.first_name} {doctor.user.last_name}"
    })
