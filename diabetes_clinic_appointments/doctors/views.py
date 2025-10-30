from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, JsonResponse, FileResponse, HttpResponseForbidden
from .forms import AppointmentNotesForm, AppointmentAttachmentForm

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


@login_required
def patient_detail(request, patient_id):
    """FR-14: Podejrzenie karty pacjenta przez lekarza"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    # Get patient and verify doctor has access (had appointments with this patient)
    from appointments.models import Appointment
    from patients.models import Patient

    patient = get_object_or_404(Patient, id=patient_id)

    # Verify doctor has access to this patient (had appointments together)
    has_access = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).exists()

    if not has_access:
        raise Http404("Nie masz uprawnień do przeglądania tej karty pacjenta.")

    # Get appointment history for this patient-doctor combination
    appointments_history = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by('-appointment_date')

    # Paginate appointment history
    paginator = Paginator(appointments_history, 10)  # 10 appointments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics for this patient with this doctor
    total_appointments = appointments_history.count()
    completed_appointments = appointments_history.filter(status='completed').count()
    cancelled_appointments = appointments_history.filter(status='cancelled').count()
    scheduled_appointments = appointments_history.filter(
        status='scheduled',
        appointment_date__gte=timezone.now()
    ).count()

    # Last and next appointments
    last_appointment = appointments_history.filter(status='completed').first()
    next_appointment = appointments_history.filter(
        status='scheduled',
        appointment_date__gte=timezone.now()
    ).order_by('appointment_date').first()

    # Appointments by status
    appointments_by_status = {
        'completed': appointments_history.filter(status='completed'),
        'scheduled': appointments_history.filter(status='scheduled'),
        'cancelled': appointments_history.filter(status='cancelled'),
        'no_show': appointments_history.filter(status='no_show'),
    }

    context = {
        'doctor': doctor,
        'patient': patient,
        'page_obj': page_obj,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'scheduled_appointments': scheduled_appointments,
        'last_appointment': last_appointment,
        'next_appointment': next_appointment,
        'appointments_by_status': appointments_by_status,
    }

    return render(request, 'doctors/patient_detail.html', context)


@login_required
def edit_appointment_notes(request, appointment_id):
    """Widok dla lekarza do edycji notatek z wizyty"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    # Get appointment and verify doctor has access
    from appointments.models import Appointment, AppointmentAttachment

    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verify this appointment belongs to this doctor
    if appointment.doctor != doctor:
        raise Http404("Nie masz uprawnień do edycji tej wizyty.")

    # Handle file upload form submission
    if request.method == 'POST' and 'upload_attachment' in request.POST:
        attachment_form = AppointmentAttachmentForm(request.POST, request.FILES)
        if attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.appointment = appointment
            attachment.uploaded_by = doctor
            attachment.save()
            messages.success(request, f'Załącznik "{attachment.filename}" został dodany pomyślnie!')
            return redirect(request.path + f'?return_to={request.GET.get("return_to", "patient_detail")}')
        else:
            messages.error(request, 'Błąd podczas przesyłania załącznika.')

    # Handle notes form submission
    elif request.method == 'POST':
        form = AppointmentNotesForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notatki zostały zapisane pomyślnie!')

            # Check if there's a return_to parameter
            return_to = request.GET.get('return_to', 'patient_detail')
            if return_to == 'upcoming':
                return redirect('doctors:upcoming_appointments')
            else:
                return redirect('doctors:patient_detail', patient_id=appointment.patient.id)
        else:
            messages.error(request, 'Wystąpił błąd podczas zapisywania notatek.')

    # GET request or form errors
    if request.method != 'POST':
        form = AppointmentNotesForm(instance=appointment)
        attachment_form = AppointmentAttachmentForm()
    else:
        # Re-initialize forms if there were errors
        if 'upload_attachment' not in request.POST:
            attachment_form = AppointmentAttachmentForm()
        else:
            form = AppointmentNotesForm(instance=appointment)

    # Get existing attachments
    attachments = appointment.attachments.all()

    # Pass return_to parameter to template
    return_to = request.GET.get('return_to', 'patient_detail')

    context = {
        'doctor': doctor,
        'appointment': appointment,
        'form': form,
        'attachment_form': attachment_form,
        'attachments': attachments,
        'patient': appointment.patient,
        'return_to': return_to,
    }

    return render(request, 'doctors/edit_appointment_notes.html', context)


@login_required
def view_appointment_notes(request, appointment_id):
    """Widok do podglądu notatek z wizyty (read-only)"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    # Get appointment and verify doctor has access
    from appointments.models import Appointment

    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verify this appointment belongs to this doctor
    if appointment.doctor != doctor:
        raise Http404("Nie masz uprawnień do przeglądania tej wizyty.")

    context = {
        'doctor': doctor,
        'appointment': appointment,
        'patient': appointment.patient,
    }

    return render(request, 'doctors/view_appointment_notes.html', context)


@login_required
def delete_attachment(request, attachment_id):
    """Widok do usuwania załącznika"""
    if not request.user.is_doctor():
        return HttpResponseForbidden("Nie masz uprawnień do wykonania tej akcji.")

    doctor = request.user.doctor_profile

    from appointments.models import AppointmentAttachment

    attachment = get_object_or_404(AppointmentAttachment, id=attachment_id)

    # Verify doctor has access to this appointment
    if attachment.appointment.doctor != doctor:
        return HttpResponseForbidden("Nie masz uprawnień do usunięcia tego załącznika.")

    if request.method == 'POST':
        appointment_id = attachment.appointment.id
        filename = attachment.filename

        # Delete the file from storage
        if attachment.file:
            attachment.file.delete(save=False)

        # Delete the database record
        attachment.delete()

        messages.success(request, f'Załącznik "{filename}" został usunięty.')

        # Redirect back to notes edit page
        return_to = request.GET.get('return_to', 'patient_detail')
        return redirect(f'/doctors/appointment/{appointment_id}/notes/?return_to={return_to}')

    # If GET request, show confirmation page
    context = {
        'doctor': doctor,
        'attachment': attachment,
        'appointment': attachment.appointment,
    }
    return render(request, 'doctors/confirm_delete_attachment.html', context)


@login_required
def download_attachment(request, attachment_id):
    """Widok do pobierania załącznika"""
    if not request.user.is_doctor():
        return HttpResponseForbidden("Nie masz uprawnień do wykonania tej akcji.")

    doctor = request.user.doctor_profile

    from appointments.models import AppointmentAttachment

    attachment = get_object_or_404(AppointmentAttachment, id=attachment_id)

    # Verify doctor has access to this appointment
    if attachment.appointment.doctor != doctor:
        return HttpResponseForbidden("Nie masz uprawnień do pobrania tego załącznika.")

    # Serve the file
    try:
        response = FileResponse(attachment.file.open('rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        return response
    except Exception as e:
        messages.error(request, f'Błąd podczas pobierania pliku: {str(e)}')
        return redirect('doctors:edit_appointment_notes', appointment_id=attachment.appointment.id)
