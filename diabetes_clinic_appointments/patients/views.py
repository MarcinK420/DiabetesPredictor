from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if not request.user.is_patient():
        return redirect('authentication:login')
    return render(request, 'patients/dashboard.html')
