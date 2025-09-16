from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Attribute URLs
    path('attributes/', views.AttributeListView.as_view(), name='attribute_list'),
    path('attributes/create/', views.AttributeCreateView.as_view(), name='attribute_create'),
    path('attributes/<int:pk>/', views.AttributeDetailView.as_view(), name='attribute_detail'),
    path('attributes/<int:pk>/update/', views.AttributeUpdateView.as_view(), name='attribute_update'),
    path('attributes/<int:pk>/delete/', views.AttributeDeleteView.as_view(), name='attribute_delete'),
    
    # Product URLs
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
]