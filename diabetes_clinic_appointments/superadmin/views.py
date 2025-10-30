from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from django.utils import timezone
from datetime import timedelta
from .forms import CreateDoctorForm

def is_superuser(user):
    """Sprawdza czy użytkownik jest superadminem"""
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def dashboard(request):
    """Panel główny superadmina"""
    total_users = User.objects.count()
    total_patients = User.objects.filter(user_type='patient').count()
    total_doctors = User.objects.filter(user_type='doctor').count()
    locked_accounts = User.objects.filter(account_locked_until__isnull=False, account_locked_until__gt=timezone.now()).count()

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'locked_accounts': locked_accounts,
    }
    return render(request, 'superadmin/dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def user_list(request):
    """Lista wszystkich użytkowników"""
    search_query = request.GET.get('search', '')
    user_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    users = User.objects.all().order_by('-date_joined')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if user_type:
        users = users.filter(user_type=user_type)

    if status == 'active':
        users = users.filter(is_active=True, account_locked_until__isnull=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'locked':
        users = users.filter(account_locked_until__isnull=False, account_locked_until__gt=timezone.now())

    context = {
        'users': users,
        'search_query': search_query,
        'user_type': user_type,
        'status': status,
    }
    return render(request, 'superadmin/user_list.html', context)

@login_required
@user_passes_test(is_superuser)
def user_detail(request, user_id):
    """Szczegóły użytkownika"""
    user = get_object_or_404(User, id=user_id)

    # Pobierz powiązane dane
    patient_data = None
    doctor_data = None

    if user.is_patient():
        try:
            patient_data = Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            pass
    elif user.is_doctor():
        try:
            doctor_data = Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            pass

    context = {
        'selected_user': user,
        'patient_data': patient_data,
        'doctor_data': doctor_data,
    }
    return render(request, 'superadmin/user_detail.html', context)

@login_required
@user_passes_test(is_superuser)
def toggle_user_status(request, user_id):
    """Aktywuj/dezaktywuj użytkownika"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # Nie pozwól na dezaktywację własnego konta
        if user.id == request.user.id:
            messages.error(request, 'Nie możesz dezaktywować własnego konta.')
            return redirect('superadmin:user_detail', user_id=user_id)

        user.is_active = not user.is_active
        user.save()

        status = 'aktywowane' if user.is_active else 'dezaktywowane'
        messages.success(request, f'Konto użytkownika {user.username} zostało {status}.')

    return redirect('superadmin:user_detail', user_id=user_id)

@login_required
@user_passes_test(is_superuser)
def unlock_user_account(request, user_id):
    """Odblokuj konto użytkownika"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.reset_failed_login()
        messages.success(request, f'Konto użytkownika {user.username} zostało odblokowane.')

    return redirect('superadmin:user_detail', user_id=user_id)

@login_required
@user_passes_test(is_superuser)
def lock_user_account(request, user_id):
    """Ręcznie zablokuj konto użytkownika"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # Nie pozwól na zablokowanie własnego konta
        if user.id == request.user.id:
            messages.error(request, 'Nie możesz zablokować własnego konta.')
            return redirect('superadmin:user_detail', user_id=user_id)

        # Zablokuj konto na 24 godziny
        user.account_locked_until = timezone.now() + timedelta(hours=24)
        user.save()
        messages.success(request, f'Konto użytkownika {user.username} zostało zablokowane na 24 godziny.')

    return redirect('superadmin:user_detail', user_id=user_id)

@login_required
@user_passes_test(is_superuser)
def change_user_role(request, user_id):
    """Zmień rolę użytkownika"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('new_role')

        # Nie pozwól na zmianę roli własnego konta
        if user.id == request.user.id:
            messages.error(request, 'Nie możesz zmienić roli własnego konta.')
            return redirect('superadmin:user_detail', user_id=user_id)

        if new_role in ['patient', 'doctor']:
            old_role = user.user_type
            user.user_type = new_role
            user.save()
            messages.success(request, f'Rola użytkownika {user.username} została zmieniona z {old_role} na {new_role}.')
        else:
            messages.error(request, 'Nieprawidłowa rola.')

    return redirect('superadmin:user_detail', user_id=user_id)

@login_required
@user_passes_test(is_superuser)
def toggle_superuser_status(request, user_id):
    """Nadaj/odbierz uprawnienia superużytkownika"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # Nie pozwól na odebranie sobie uprawnień
        if user.id == request.user.id:
            messages.error(request, 'Nie możesz odebrać sobie uprawnień superużytkownika.')
            return redirect('superadmin:user_detail', user_id=user_id)

        user.is_superuser = not user.is_superuser
        user.is_staff = user.is_superuser  # Automatycznie nadaj/odbierz is_staff
        user.save()

        status = 'nadane' if user.is_superuser else 'odebrane'
        messages.success(request, f'Uprawnienia superużytkownika dla {user.username} zostały {status}.')

    return redirect('superadmin:user_detail', user_id=user_id)

@login_required
@user_passes_test(is_superuser)
def delete_user(request, user_id):
    """Usuń użytkownika"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # Nie pozwól na usunięcie własnego konta
        if user.id == request.user.id:
            messages.error(request, 'Nie możesz usunąć własnego konta.')
            return redirect('superadmin:user_detail', user_id=user_id)

        username = user.username
        user.delete()
        messages.success(request, f'Użytkownik {username} został usunięty.')
        return redirect('superadmin:user_list')

    return redirect('superadmin:user_detail', user_id=user_id)

@login_required
@user_passes_test(is_superuser)
def reset_user_password(request, user_id):
    """Resetuj hasło użytkownika"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_password = request.POST.get('new_password')

        if new_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Hasło użytkownika {user.username} zostało zresetowane.')
        else:
            messages.error(request, 'Podaj nowe hasło.')

    return redirect('superadmin:user_detail', user_id=user_id)

@login_required
@user_passes_test(is_superuser)
def create_doctor(request):
    """Utwórz nowe konto lekarza"""
    if request.method == 'POST':
        form = CreateDoctorForm(request.POST)
        if form.is_valid():
            user, doctor = form.save()
            messages.success(
                request,
                f'Konto lekarza {user.get_full_name()} zostało utworzone pomyślnie! '
                f'Login: {user.username}'
            )
            return redirect('superadmin:user_detail', user_id=user.id)
        else:
            messages.error(request, 'Wystąpiły błędy w formularzu. Sprawdź poniższe pola.')
    else:
        form = CreateDoctorForm()

    context = {
        'form': form,
    }
    return render(request, 'superadmin/create_doctor.html', context)
