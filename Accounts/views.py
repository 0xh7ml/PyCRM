from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def accounts_dashboard(request):
    """Accounts dashboard view - Under Construction"""
    context = {
        'page_title': 'Accounts Dashboard',
        'module_name': 'Accounts',
        'under_construction': True
    }
    return render(request, 'accounts/dashboard.html', context)
