from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from .models import User, FarmerProfile

def register(request):
    """User registration view handles both regular users and farmers."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('accounts:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('accounts:register')
        
        user = User.objects.create_user(
            username=username, email=email, password=password,
            user_type=user_type, phone=phone, location=location
        )
        
        if user_type == 'farmer':
            farm_name = request.POST.get('farm_name')
            farm_size_str = request.POST.get('farm_size', '0')
            specialization = request.POST.get('specialization')
            try:
                farm_size = float(farm_size_str) if farm_size_str else 0
            except (ValueError, TypeError):
                farm_size = 0
            
            FarmerProfile.objects.create(
                user=user, farm_name=farm_name,
                farm_size=farm_size, specialization=specialization
            )
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')

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
    farmer_profile = getattr(request.user, 'farmerprofile', None)
    context = {'user': request.user, 'farmer_profile': farmer_profile}
    return render(request, 'accounts/dashboard.html', context)

@login_required
def edit_profile(request):
    """User profile edit view."""
    user = request.user
    farmer_profile = getattr(user, 'farmerprofile', None)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.location = request.POST.get('location')
        user.save()

        if user.user_type == 'farmer' and farmer_profile:
            farmer_profile.farm_name = request.POST.get('farm_name')
            farmer_profile.specialization = request.POST.get('specialization')
            farm_size_str = request.POST.get('farm_size')
            try:
                farmer_profile.farm_size = float(farm_size_str) if farm_size_str else 0
            except (ValueError, TypeError):
                pass
            farmer_profile.save()

        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/edit_profile.html', {'user': user, 'farmer_profile': farmer_profile})