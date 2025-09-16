from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Auth.urls')),
    path('dashboard/', include('Dashboard.urls')),
    path('crm/', include('CRM.urls')),
    path('products/', include('Product.urls')),
    path('oms/', include('OMS.urls')),
    path('inventory/', include('Inventory.urls')),
    path('reports/', include('Reports.urls')),
    path('accounts/', include('Accounts.urls')),
    path('hrm/', include('HRM.urls')),
    path('', include('Auth.urls')),  # Root URL redirects to auth
]
