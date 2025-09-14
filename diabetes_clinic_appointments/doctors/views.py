from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q

@login_required
def dashboard(request):
    """FR-11: Strona główna lekarza"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    # Get dashboard statistics
    from appointments.models import Appointment

    # Today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='scheduled',
        appointment_date__date=timezone.now().date()
    ).count()

    # Next 7 days appointments
    next_week = timezone.now() + timezone.timedelta(days=7)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='scheduled',
        appointment_date__gte=timezone.now(),
        appointment_date__lte=next_week
    ).count()

    # Total patients (unique patients who had appointments)
    total_patients = Appointment.objects.filter(
        doctor=doctor
    ).values('patient').distinct().count()

    # Next appointment
    next_appointment = Appointment.objects.filter(
        doctor=doctor,
        status='scheduled',
        appointment_date__gte=timezone.now()
    ).order_by('appointment_date').first()

    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_patients': total_patients,
        'next_appointment': next_appointment,
    }

    return render(request, 'doctors/dashboard.html', context)


@login_required
def upcoming_appointments(request):
    """FR-12: Najbliższe wizyty lekarza"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    # Get upcoming appointments (scheduled, in future)
    from appointments.models import Appointment

    appointments = Appointment.objects.filter(
        doctor=doctor,
        status='scheduled',
        appointment_date__gte=timezone.now()
    ).select_related('patient__user').order_by('appointment_date')

    # Group appointments by date for better display
    appointments_by_date = {}
    for appointment in appointments:
        date_key = appointment.appointment_date.date()
        if date_key not in appointments_by_date:
            appointments_by_date[date_key] = []
        appointments_by_date[date_key].append(appointment)

    # Get today's appointments separately
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='scheduled',
        appointment_date__date=timezone.now().date()
    ).select_related('patient__user').order_by('appointment_date')

    # Statistics
    total_upcoming = appointments.count()
    today_count = today_appointments.count()

    # Next 7 days count
    next_week = timezone.now() + timezone.timedelta(days=7)
    week_count = appointments.filter(appointment_date__lte=next_week).count()

    context = {
        'doctor': doctor,
        'appointments_by_date': appointments_by_date,
        'today_appointments': today_appointments,
        'total_upcoming': total_upcoming,
        'today_count': today_count,
        'week_count': week_count,
        'current_date': timezone.now().date(),
    }

    return render(request, 'doctors/upcoming_appointments.html', context)


@login_required
def patients_list(request):
    """FR-13: Spis pacjentów lekarza"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    # Get all patients who had appointments with this doctor
    from appointments.models import Appointment
    from patients.models import Patient

    # Get unique patients with their appointment statistics
    patients_with_appointments = Patient.objects.filter(
        appointments__doctor=doctor
    ).annotate(
        total_appointments=Count('appointments', filter=Q(appointments__doctor=doctor)),
        scheduled_appointments=Count(
            'appointments',
            filter=Q(appointments__doctor=doctor, appointments__status='scheduled', appointments__appointment_date__gte=timezone.now())
        ),
        completed_appointments=Count(
            'appointments',
            filter=Q(appointments__doctor=doctor, appointments__status='completed')
        )
    ).select_related('user').distinct().order_by('user__last_name', 'user__first_name')

    # Get last and next appointments for each patient
    patients_data = []
    for patient in patients_with_appointments:
        last_appointment = Appointment.objects.filter(
            doctor=doctor,
            patient=patient,
            status='completed'
        ).order_by('-appointment_date').first()

        next_appointment = Appointment.objects.filter(
            doctor=doctor,
            patient=patient,
            status='scheduled',
            appointment_date__gte=timezone.now()
        ).order_by('appointment_date').first()

        patients_data.append({
            'patient': patient,
            'total_appointments': patient.total_appointments,
            'scheduled_appointments': patient.scheduled_appointments,
            'completed_appointments': patient.completed_appointments,
            'last_appointment': last_appointment,
            'next_appointment': next_appointment,
        })

    # Pagination
    paginator = Paginator(patients_data, 10)  # 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_patients = len(patients_data)
    patients_with_scheduled = sum(1 for p in patients_data if p['scheduled_appointments'] > 0)

    context = {
        'doctor': doctor,
        'page_obj': page_obj,
        'total_patients': total_patients,
        'patients_with_scheduled': patients_with_scheduled,
    }

    return render(request, 'doctors/patients_list.html', context)
