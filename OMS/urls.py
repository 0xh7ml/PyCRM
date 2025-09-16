from django.urls import path
from .views import (
    OrderListView, OrderDetailView, OrderDeleteView,
    create_order_view, update_order_view, get_product_price, generate_invoice
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create/', create_order_view, name='order-create'),
    path('<int:pk>/update/', update_order_view, name='order-update'),
    path('<int:pk>/delete/', OrderDeleteView.as_view(), name='order-delete'),
    path('<int:pk>/invoice/', generate_invoice, name='order-invoice'),
    path('ajax/get-product-price/', get_product_price, name='get-product-price'),
]