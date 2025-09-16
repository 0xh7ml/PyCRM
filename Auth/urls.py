from django.urls import path
from .views import index, logout_view

urlpatterns = [
    path('', index, name='auth-login'),
    path('login/', index, name='auth-login'),
    path('logout/', logout_view, name='auth-logout'),
]