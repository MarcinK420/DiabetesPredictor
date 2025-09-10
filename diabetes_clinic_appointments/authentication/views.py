from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from .forms import PatientRegistrationForm, DoctorRegistrationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_patient():
                return redirect('patients:dashboard')
            elif user.is_doctor():
                return redirect('doctors:dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'authentication/login.html', {'form': form})

def register_choice(request):
    return render(request, 'authentication/register_choice.html')

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Konto pacjenta zostało utworzone pomyślnie!')
            return redirect('authentication:login')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'authentication/register_patient.html', {'form': form})

def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Konto lekarza zostało utworzone pomyślnie!')
            return redirect('authentication:login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'authentication/register_doctor.html', {'form': form})
