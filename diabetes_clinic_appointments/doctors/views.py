from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, JsonResponse, FileResponse, HttpResponseForbidden
from .forms import AppointmentNotesForm, AppointmentAttachmentForm, NoteTemplateForm, DoctorProfileForm, DiabetesPredictionForm
import sys
import os

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

    # Get sort parameters
    sort_by = request.GET.get('sort', 'name')
    sort_order = request.GET.get('order', 'asc')

    # Get filter parameters
    diabetes_filter = request.GET.get('diabetes_type', '')
    appointment_status_filter = request.GET.get('appointment_status', '')
    search_query = request.GET.get('search', '')

    # Get unique patients with their appointment statistics
    patients_query = Patient.objects.filter(
        appointments__doctor=doctor
    )

    # Apply search filter
    if search_query:
        patients_query = patients_query.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    # Apply diabetes type filter
    if diabetes_filter:
        patients_query = patients_query.filter(diabetes_type=diabetes_filter)

    patients_with_appointments = patients_query.annotate(
        total_appointments=Count('appointments', filter=Q(appointments__doctor=doctor)),
        scheduled_appointments=Count(
            'appointments',
            filter=Q(appointments__doctor=doctor, appointments__status='scheduled', appointments__appointment_date__gte=timezone.now())
        ),
        completed_appointments=Count(
            'appointments',
            filter=Q(appointments__doctor=doctor, appointments__status='completed')
        )
    ).select_related('user').distinct()

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

        patient_info = {
            'patient': patient,
            'total_appointments': patient.total_appointments,
            'scheduled_appointments': patient.scheduled_appointments,
            'completed_appointments': patient.completed_appointments,
            'last_appointment': last_appointment,
            'next_appointment': next_appointment,
        }

        # Apply appointment status filter
        if appointment_status_filter == 'with_upcoming':
            if patient.scheduled_appointments > 0:
                patients_data.append(patient_info)
        elif appointment_status_filter == 'without_upcoming':
            if patient.scheduled_appointments == 0:
                patients_data.append(patient_info)
        else:
            patients_data.append(patient_info)

    # Apply sorting to patients_data
    reverse = (sort_order == 'desc')

    if sort_by == 'name':
        patients_data.sort(key=lambda x: (x['patient'].user.last_name.lower(), x['patient'].user.first_name.lower()), reverse=reverse)
    elif sort_by == 'email':
        patients_data.sort(key=lambda x: x['patient'].user.email.lower(), reverse=reverse)
    elif sort_by == 'diabetes_type':
        patients_data.sort(key=lambda x: x['patient'].diabetes_type or '', reverse=reverse)
    elif sort_by == 'total_appointments':
        patients_data.sort(key=lambda x: x['total_appointments'], reverse=reverse)
    elif sort_by == 'last_appointment':
        patients_data.sort(key=lambda x: (x['last_appointment'].appointment_date if x['last_appointment'] else timezone.datetime.min.replace(tzinfo=timezone.get_current_timezone())), reverse=reverse)
    elif sort_by == 'next_appointment':
        patients_data.sort(key=lambda x: (x['next_appointment'].appointment_date if x['next_appointment'] else timezone.datetime.max.replace(tzinfo=timezone.get_current_timezone())), reverse=reverse)

    # Pagination
    paginator = Paginator(patients_data, 10)  # 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_patients = len(patients_data)
    patients_with_scheduled = sum(1 for p in patients_data if p['scheduled_appointments'] > 0)

    # Build filter params string for pagination and sorting
    filter_params = ''
    if search_query:
        filter_params += f'&search={search_query}'
    if diabetes_filter:
        filter_params += f'&diabetes_type={diabetes_filter}'
    if appointment_status_filter:
        filter_params += f'&appointment_status={appointment_status_filter}'

    context = {
        'doctor': doctor,
        'page_obj': page_obj,
        'total_patients': total_patients,
        'patients_with_scheduled': patients_with_scheduled,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'search_query': search_query,
        'diabetes_filter': diabetes_filter,
        'appointment_status_filter': appointment_status_filter,
        'filter_params': filter_params,
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

    # Get sort parameters
    sort_by = request.GET.get('sort', 'date')
    sort_order = request.GET.get('order', 'desc')

    # Get filter parameters
    status_filter = request.GET.get('status', '')

    # Get appointment history for this patient-doctor combination
    appointments_history = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    )

    # Apply filter
    if status_filter:
        appointments_history = appointments_history.filter(status=status_filter)

    # Apply sorting
    order_prefix = '-' if sort_order == 'desc' else ''

    if sort_by == 'date':
        appointments_history = appointments_history.order_by(f'{order_prefix}appointment_date')
    elif sort_by == 'status':
        appointments_history = appointments_history.order_by(f'{order_prefix}status')
    elif sort_by == 'reason':
        appointments_history = appointments_history.order_by(f'{order_prefix}reason')
    else:
        appointments_history = appointments_history.order_by('-appointment_date')

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

    # Build filter params string for pagination and sorting
    filter_params = ''
    if status_filter:
        filter_params += f'&status={status_filter}'

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
        'sort_by': sort_by,
        'sort_order': sort_order,
        'status_filter': status_filter,
        'filter_params': filter_params,
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

    # Get available note templates
    from appointments.models import NoteTemplate
    templates = NoteTemplate.objects.filter(is_active=True).order_by('category', 'name')

    # Pass return_to parameter to template
    return_to = request.GET.get('return_to', 'patient_detail')

    context = {
        'doctor': doctor,
        'appointment': appointment,
        'form': form,
        'attachment_form': attachment_form,
        'attachments': attachments,
        'templates': templates,
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

    # Get attachments
    attachments = appointment.attachments.all()

    context = {
        'doctor': doctor,
        'appointment': appointment,
        'patient': appointment.patient,
        'attachments': attachments,
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


# ============================================
# Note Templates Management Views
# ============================================

@login_required
def list_templates(request):
    """Lista szablonów notatek"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    from appointments.models import NoteTemplate

    # Get all active templates, grouped by category
    templates = NoteTemplate.objects.filter(is_active=True).order_by('category', 'name')

    # Group templates by category
    templates_by_category = {}
    for template in templates:
        category = template.get_category_display()
        if category not in templates_by_category:
            templates_by_category[category] = []
        templates_by_category[category].append(template)

    context = {
        'doctor': doctor,
        'templates_by_category': templates_by_category,
        'total_templates': templates.count(),
    }

    return render(request, 'doctors/list_templates.html', context)


@login_required
def create_template(request):
    """Tworzenie nowego szablonu notatki"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    if request.method == 'POST':
        form = NoteTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = doctor
            template.save()
            messages.success(request, f'Szablon "{template.name}" został utworzony.')
            return redirect('doctors:list_templates')
    else:
        form = NoteTemplateForm()

    context = {
        'doctor': doctor,
        'form': form,
        'action': 'create',
    }

    return render(request, 'doctors/template_form.html', context)


@login_required
def edit_template(request, template_id):
    """Edycja szablonu notatki"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    from appointments.models import NoteTemplate

    template = get_object_or_404(NoteTemplate, id=template_id)

    if request.method == 'POST':
        form = NoteTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, f'Szablon "{template.name}" został zaktualizowany.')
            return redirect('doctors:list_templates')
    else:
        form = NoteTemplateForm(instance=template)

    context = {
        'doctor': doctor,
        'form': form,
        'template': template,
        'action': 'edit',
    }

    return render(request, 'doctors/template_form.html', context)


@login_required
def delete_template(request, template_id):
    """Usuwanie szablonu notatki"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    from appointments.models import NoteTemplate

    template = get_object_or_404(NoteTemplate, id=template_id)

    if request.method == 'POST':
        template_name = template.name
        template.delete()
        messages.success(request, f'Szablon "{template_name}" został usunięty.')
        return redirect('doctors:list_templates')

    context = {
        'doctor': doctor,
        'template': template,
    }

    return render(request, 'doctors/confirm_delete_template.html', context)


@login_required
def get_template_content(request, template_id):
    """API endpoint do pobierania treści szablonu (AJAX)"""
    if not request.user.is_doctor():
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)

    from appointments.models import NoteTemplate

    template = get_object_or_404(NoteTemplate, id=template_id, is_active=True)

    return JsonResponse({
        'success': True,
        'content': template.content,
        'name': template.name,
    })


# ============================================
# Doctor Profile Views
# ============================================

@login_required
def doctor_profile(request):
    """Widok profilu lekarza (tylko do odczytu)"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    context = {
        'doctor': doctor,
        'user': request.user,
    }

    return render(request, 'doctors/profile.html', context)


@login_required
def edit_profile(request):
    """Widok edycji profilu lekarza"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil został zaktualizowany pomyślnie!')
            return redirect('doctors:doctor_profile')
        else:
            messages.error(request, 'Wystąpił błąd podczas zapisywania profilu.')
    else:
        form = DoctorProfileForm(instance=doctor, user=request.user)

    context = {
        'doctor': doctor,
        'form': form,
    }

    return render(request, 'doctors/edit_profile.html', context)


# ============================================
# Diabetes Risk Prediction Views
# ============================================

@login_required
def diabetes_risk_assessment(request, appointment_id):
    """Widok do oceny ryzyka cukrzycy dla zakończonej wizyty"""
    if not request.user.is_doctor():
        return redirect('authentication:login')

    doctor = request.user.doctor_profile

    # Get appointment and verify doctor has access
    from appointments.models import Appointment, DiabetesPrediction

    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verify this appointment belongs to this doctor
    if appointment.doctor != doctor:
        raise Http404("Nie masz uprawnień do tej wizyty.")

    # Check if appointment is completed
    if appointment.status != 'completed':
        messages.warning(request, 'Ocena ryzyka jest dostępna tylko dla zakończonych wizyt.')
        return redirect('doctors:patient_detail', patient_id=appointment.patient.id)

    # Check if prediction already exists
    existing_prediction = None
    try:
        existing_prediction = DiabetesPrediction.objects.get(appointment=appointment)
    except DiabetesPrediction.DoesNotExist:
        pass

    # Handle form submission
    if request.method == 'POST':
        form = DiabetesPredictionForm(request.POST, instance=existing_prediction)
        if form.is_valid():
            # Get form data
            patient_data = {
                'pregnancies': form.cleaned_data['pregnancies'],
                'glucose': form.cleaned_data['glucose'],
                'blood_pressure': form.cleaned_data['blood_pressure'],
                'skin_thickness': form.cleaned_data['skin_thickness'],
                'insulin': form.cleaned_data['insulin'],
                'bmi': form.cleaned_data['bmi'],
                'diabetes_pedigree': form.cleaned_data['diabetes_pedigree'],
                'age': form.cleaned_data['age'],
            }

            # Import and use the predictor
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ml'))
            from diabetes_predictor import DiabetesPredictor

            try:
                # Initialize predictor and get prediction
                predictor = DiabetesPredictor()
                result = predictor.predict_with_interpretation(patient_data)

                # Save prediction
                prediction = form.save(commit=False)
                prediction.appointment = appointment
                prediction.probability = result['probability']
                prediction.percentage = result['percentage']
                prediction.risk_level = result['risk_level']
                prediction.risk_color = result['risk_color']
                prediction.created_by = doctor
                prediction.save()

                messages.success(request, 'Ocena ryzyka cukrzycy została wygenerowana pomyślnie!')

                # Redirect to show results
                context = {
                    'doctor': doctor,
                    'appointment': appointment,
                    'patient': appointment.patient,
                    'form': form,
                    'prediction': prediction,
                    'show_results': True,
                }
                return render(request, 'doctors/diabetes_risk_assessment.html', context)

            except Exception as e:
                messages.error(request, f'Błąd podczas generowania predykcji: {str(e)}')
                form = DiabetesPredictionForm(instance=existing_prediction)
        else:
            messages.error(request, 'Wystąpiły błędy w formularzu. Sprawdź wprowadzone dane.')
    else:
        # GET request - initialize form
        if existing_prediction:
            form = DiabetesPredictionForm(instance=existing_prediction)
        else:
            # Pre-fill age from patient data if available
            initial_data = {}
            if hasattr(appointment.patient, 'get_age'):
                initial_data['age'] = appointment.patient.get_age()
            form = DiabetesPredictionForm(initial=initial_data)

    context = {
        'doctor': doctor,
        'appointment': appointment,
        'patient': appointment.patient,
        'form': form,
        'prediction': existing_prediction,
        'show_results': False,
    }

    return render(request, 'doctors/diabetes_risk_assessment.html', context)
