from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import User, FarmerProfile, InputSupplierProfile, TransporterProfile, VerificationRequest
from .constants import UGANDA_DISTRICT_CHOICES, SPECIALIZATION_CHOICES
from .forms import RegisterForm

def register(request):
    """User registration — validated through RegisterForm."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                username=cd['username'],
                email=cd['email'],
                password=cd['password'],
                user_type=cd['user_type'],
                phone=cd.get('phone', ''),
                location=cd.get('location', ''),
            )

            if cd['user_type'] == 'farmer':
                FarmerProfile.objects.create(
                    user=user,
                    farm_name=cd.get('farm_name') or f"{user.username}'s Farm",
                    farm_size=cd.get('farm_size') or 0,
                    specialization=cd.get('specialization') or 'Mixed Farming',
                )
            elif cd['user_type'] == 'transporter':
                # Create a basic transporter profile; user can complete it later
                TransporterProfile.objects.create(
                    user=user,
                    vehicle_type='pickup',
                    capacity_kg=500,
                    coverage_districts=cd.get('location', 'Kampala'),
                )

            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
        # Form is invalid — re-render with errors
        return render(request, 'accounts/register.html', {'form': form})

    form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('marketplace:home')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'accounts/login.html')

@login_required
@never_cache
@require_POST
def logout_view(request):
    """Secure logout: Requires POST and clears cache."""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    response = redirect('accounts:login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def dashboard(request):
    """User dashboard view."""
    farmer_profile = getattr(request.user, 'farmer_profile', None)
    transporter_profile = getattr(request.user, 'transporter_profile', None)
    try:
        verification = request.user.verification_request
    except VerificationRequest.DoesNotExist:
        verification = None
    context = {
        'user': request.user,
        'farmer_profile': farmer_profile,
        'transporter_profile': transporter_profile,
        'verification': verification,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def submit_verification(request):
    """Allow users to submit an identity verification request."""
    # If already approved, no need to re-submit
    try:
        vr = request.user.verification_request
        if vr.status == 'approved':
            messages.info(request, 'Your account is already verified!')
            return redirect('accounts:dashboard')
    except VerificationRequest.DoesNotExist:
        vr = None

    if request.method == 'POST':
        notes = request.POST.get('notes', '').strip()
        business_reg = request.POST.get('business_reg_number', '').strip()

        if vr is None:
            vr = VerificationRequest(user=request.user)

        vr.notes = notes
        vr.business_reg_number = business_reg
        vr.status = 'pending'

        if request.FILES.get('national_id_image'):
            vr.national_id_image = request.FILES['national_id_image']
        if request.FILES.get('farm_or_business_photo'):
            vr.farm_or_business_photo = request.FILES['farm_or_business_photo']

        vr.save()
        messages.success(
            request,
            'Verification request submitted! We will review it within 2 business days.'
        )
        return redirect('accounts:verification_status')

    return render(request, 'accounts/submit_verification.html', {'vr': vr})


@login_required
def verification_status(request):
    """Show the current status of the user's verification request."""
    try:
        vr = request.user.verification_request
    except VerificationRequest.DoesNotExist:
        vr = None
    return render(request, 'accounts/verification_status.html', {'vr': vr})

@login_required
def edit_profile(request):
    """User profile edit view — supports Personal Info, Business Details, and Security tabs."""
    user = request.user
    farmer_profile   = getattr(user, 'farmerprofile',  None)
    supplier_profile = getattr(user, 'supplier_profile', None)

    section = request.POST.get('section', 'personal')   # which tab submitted

    if request.method == 'POST':

        # ── PERSONAL INFO ─────────────────────────────────────
        if section in ('personal', ''):
            user.first_name      = request.POST.get('first_name', '').strip()
            user.last_name       = request.POST.get('last_name',  '').strip()
            user.email           = request.POST.get('email',      '').strip()
            user.phone           = request.POST.get('phone',      '').strip()
            user.whatsapp_number = request.POST.get('whatsapp_number', '').strip()
            user.location        = request.POST.get('location',   '').strip()
            user.address         = request.POST.get('address',    '').strip()
            user.district        = request.POST.get('district',   '').strip()

            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES['profile_picture']

            user.save()
            messages.success(request, 'Personal information updated successfully!')
            return redirect('/accounts/edit-profile/?tab=personal')

        # ── BUSINESS DETAILS ──────────────────────────────────
        elif section == 'business':
            if user.user_type == 'farmer':
                if not farmer_profile:
                    farmer_profile = FarmerProfile(user=user, farm_size=0)
                farmer_profile.farm_name     = request.POST.get('farm_name', '').strip()
                farmer_profile.specialization = request.POST.get('specialization', '').strip()
                farm_size_str = request.POST.get('farm_size', '0')
                try:
                    farmer_profile.farm_size = float(farm_size_str) if farm_size_str else 0
                except (ValueError, TypeError):
                    farmer_profile.farm_size = 0
                farmer_profile.save()

            elif user.user_type == 'input_supplier':
                if not supplier_profile:
                    supplier_profile = InputSupplierProfile(user=user, specialization='Other')
                supplier_profile.company_name     = request.POST.get('company_name', '').strip()
                supplier_profile.business_license = request.POST.get('business_license', '').strip()
                supplier_profile.specialization   = request.POST.get('supplier_specialization', '').strip()
                supplier_profile.save()

            messages.success(request, 'Business details updated successfully!')
            return redirect('/accounts/edit-profile/?tab=business')

        # ── SECURITY / PASSWORD ───────────────────────────────
        elif section == 'security':
            current_password = request.POST.get('current_password', '')
            new_password     = request.POST.get('new_password',     '')
            confirm_password = request.POST.get('confirm_password', '')

            if current_password or new_password or confirm_password:
                if not user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect.')
                elif new_password != confirm_password:
                    messages.error(request, 'New passwords do not match.')
                elif len(new_password) < 8:
                    messages.error(request, 'Password must be at least 8 characters.')
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)   # keep user logged in
                    messages.success(request, 'Password changed successfully!')
            else:
                messages.info(request, 'No password changes were made.')

            return redirect('/accounts/edit-profile/?tab=security')

    # ── GET: build context ────────────────────────────────────
    # Flatten grouped district choices so the template can loop simply
    flat_districts = []
    for region_or_val in UGANDA_DISTRICT_CHOICES:
        if isinstance(region_or_val[1], (list, tuple)):
            # It's a grouped optgroup (region_name, [(val, label), ...])
            flat_districts.extend(region_or_val[1])
        else:
            flat_districts.append(region_or_val)

    context = {
        'user':                  user,
        'farmer_profile':        farmer_profile,
        'supplier_profile':      supplier_profile,
        'district_choices':      UGANDA_DISTRICT_CHOICES,   # keep groups for optgroup rendering
        'flat_district_choices': flat_districts,
        'specialization_choices': SPECIALIZATION_CHOICES,
    }
    return render(request, 'accounts/edit_profile.html', context)