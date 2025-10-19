from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import PatientRegistrationForm, DoctorRegistrationForm
from .models import User
from django.utils import timezone

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        # Sprawdź czy użytkownik istnieje
        try:
            user = User.objects.get(username=username)

            # Sprawdź czy konto jest zablokowane
            if user.is_account_locked():
                time_remaining = (user.account_locked_until - timezone.now()).seconds // 60 + 1
                messages.error(request, f'Twoje konto jest zablokowane z powodu zbyt wielu nieudanych prób logowania. Spróbuj ponownie za {time_remaining} minut.')
                return render(request, 'authentication/login.html', {'form': AuthenticationForm()})
        except User.DoesNotExist:
            pass

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Resetuj licznik nieudanych prób logowania
            user.reset_failed_login()

            login(request, user)

            # Sprawdź czy użytkownik jest superadminem
            if user.is_superuser:
                return redirect('superadmin:dashboard')
            elif user.is_patient():
                return redirect('patients:dashboard')
            elif user.is_doctor():
                return redirect('doctors:dashboard')
        else:
            # Zwiększ licznik nieudanych prób logowania
            try:
                user = User.objects.get(username=username)
                user.increment_failed_login()

                remaining_attempts = 5 - user.failed_login_attempts
                if remaining_attempts > 0:
                    messages.error(request, f'Nieprawidłowa nazwa użytkownika lub hasło. Pozostało prób: {remaining_attempts}')
                else:
                    messages.error(request, 'Twoje konto zostało zablokowane na 15 minut z powodu zbyt wielu nieudanych prób logowania.')
            except User.DoesNotExist:
                messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')
    else:
        form = AuthenticationForm()

    return render(request, 'authentication/login.html', {'form': form})

def register_choice(request):
    return render(request, 'authentication/register_choice.html')

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Konto pacjenta zostało utworzone pomyślnie!')
                return redirect('authentication:login')
            except Exception as e:
                # Handle database errors (like duplicate PESEL)
                if 'UNIQUE constraint failed' in str(e) or 'duplicate' in str(e).lower():
                    form.add_error('pesel', 'Pacjent z tym numerem PESEL już istnieje w systemie.')
                else:
                    messages.error(request, 'Wystąpił błąd podczas tworzenia konta. Spróbuj ponownie.')
    else:
        form = PatientRegistrationForm()

    return render(request, 'authentication/register_patient.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Zostałeś pomyślnie wylogowany.')
    return redirect('authentication:login')
