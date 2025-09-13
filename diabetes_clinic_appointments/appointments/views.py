from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentBookingForm

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
