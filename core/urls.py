from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('Dashboard.urls')),
    path('crm/', include('CRM.urls')),
    path('products/', include('Product.urls')),
    path('oms/', include('OMS.urls')),
    path('inventory/', include('Inventory.urls')),
    path('reports/', include('Reports.urls')),
    path('', include('Dashboard.urls')),  # Root URL redirects to dashboard
]
