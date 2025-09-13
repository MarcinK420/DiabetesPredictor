from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Appointment

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
