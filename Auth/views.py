from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    """Login view"""
    # Check if user is authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:  # Check if the user is active
                login(request, user)    
                return redirect('dashboard')
            else:
                messages.error(request, "Your account is inactive.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'auth/index.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('auth-login')
