from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, FarmerProfile

def register(request):
    """
    User registration view
    """
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        
        # Basic validation
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('accounts:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('accounts:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('accounts:register')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            phone=phone,
            location=location
        )
        
        # If farmer, create farmer profile
        if user_type == 'farmer':
            farm_name = request.POST.get('farm_name')
            farm_size_str = request.POST.get('farm_size', '0')
            specialization = request.POST.get('specialization')
            
            # Handle empty farm_size - convert to 0 if empty
            try:
                farm_size = float(farm_size_str) if farm_size_str else 0
            except (ValueError, TypeError):
                farm_size = 0
            
            FarmerProfile.objects.create(
                user=user,
                farm_name=farm_name,
                farm_size=farm_size,
                specialization=specialization
            )
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')


def user_login(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


@login_required
def dashboard(request):
    """
    User dashboard view
    """
    context = {
        'user': request.user
    }
    return render(request, 'accounts/dashboard.html', context)