from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crm/', include('CRM.urls')),
    path('products/', include('Product.urls')),
    path('oms/', include('OMS.urls')),
]
