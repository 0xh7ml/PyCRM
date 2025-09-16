from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def hrm_dashboard(request):
    """HRM dashboard view - Under Construction"""
    context = {
        'page_title': 'HRM Dashboard',
        'module_name': 'Human Resources',
        'under_construction': True
    }
    return render(request, 'hrm/dashboard.html', context)
