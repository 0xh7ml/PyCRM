from django.urls import path
from . import views

urlpatterns = [
    path('', views.hrm_dashboard, name='hrm-dashboard'),
]