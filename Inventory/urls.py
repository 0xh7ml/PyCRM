from django.urls import path
from . import views

urlpatterns = [
    # Stock In URLs
    path('stock-in/', views.stock_in_list, name='stock-in-list'),
    path('stock-in/create/', views.stock_in_create, name='stock-in-create'),
    path('stock-in/<int:pk>/', views.stock_in_detail, name='stock-in-detail'),
    path('stock-in/<int:pk>/edit/', views.stock_in_edit, name='stock-in-edit'),
    path('stock-in/<int:pk>/complete/', views.stock_in_complete, name='stock-in-complete'),
    path('stock-in/<int:pk>/delete/', views.stock_in_delete, name='stock-in-delete'),
    
    # Stock URLs
    path('stock/', views.stock_list, name='stock-list'),
    
    # AJAX URLs for product search
    path('search-product-barcode/', views.search_product_by_barcode, name='search-product-barcode'),
    path('search-products/', views.search_products, name='search-products'),
]