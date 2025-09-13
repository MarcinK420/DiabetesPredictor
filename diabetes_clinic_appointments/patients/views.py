from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
