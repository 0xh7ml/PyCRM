from django.urls import path
from . import views

urlpatterns = [
    path('vendors/', views.VendorListView.as_view(), name='vendor-list'),
    path('vendors/create/', views.VendorCreateView.as_view(), name='vendor-create'),
    path('vendors/<int:pk>/', views.VendorDetailView.as_view(), name='vendor-detail'),
    path('vendors/<int:pk>/update/', views.VendorUpdateView.as_view(), name='vendor-update'),
    path('vendors/<int:pk>/delete/', views.VendorDeleteView.as_view(), name='vendor-delete'),
]