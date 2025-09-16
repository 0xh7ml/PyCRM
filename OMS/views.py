from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.forms import formset_factory, modelformset_factory
from django.db import transaction
from .models import Order, OrderItem
from CRM.models import Vendor
from Product.models import Product
import json

class OrderListView(ListView):
    model = Order
    template_name = 'oms/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

class OrderDetailView(DetailView):
    model = Order
    template_name = 'oms/order_detail.html'
    context_object_name = 'order'

def create_order_view(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        notes = request.POST.get('notes', '')
        items_data = request.POST.get('items_data')
        
        # Debug print
        print(f"POST data: vendor_id={vendor_id}, notes={notes}, items_data={items_data}")
        
        if not vendor_id:
            messages.error(request, 'Please select a vendor.')
            vendors = Vendor.objects.all()
            products = Product.objects.filter(is_active=True)
            return render(request, 'oms/order_form.html', {'vendors': vendors, 'products': products})
        
        if not items_data:
            messages.error(request, 'Please add at least one item to the order.')
            vendors = Vendor.objects.all()
            products = Product.objects.filter(is_active=True)
            return render(request, 'oms/order_form.html', {'vendors': vendors, 'products': products})
        
        try:
            with transaction.atomic():
                vendor = get_object_or_404(Vendor, id=vendor_id)
                order = Order.objects.create(vendor=vendor, notes=notes)
                print(f"Order created with ID: {order.pk}")
                
                items = json.loads(items_data)
                print(f"Items data parsed: {items}")
                
                for item_data in items:
                    product = get_object_or_404(Product, id=item_data['product_id'])
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=int(item_data['quantity']),
                        unit_price=float(item_data['unit_price']),
                        discount_type=item_data['discount_type'],
                        discount_value=float(item_data['discount_value'])
                    )
                    print(f"OrderItem created: {order_item}")
                
                # Recalculate total
                order.calculate_total()
                print(f"Order total calculated: {order.total_amount}")
                
                messages.success(request, f'Order {order.pk} created successfully!')
                return redirect('order-detail', pk=order.pk)
                
        except json.JSONDecodeError as e:
            messages.error(request, f'Invalid items data format: {str(e)}')
        except ValueError as e:
            messages.error(request, f'Invalid number format in items: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
            print(f"Error creating order: {e}")
    
    vendors = Vendor.objects.all()
    products = Product.objects.filter(is_active=True)
    
    print(f"Available vendors: {vendors.count()}")
    print(f"Available products: {products.count()}")
    
    context = {
        'vendors': vendors,
        'products': products,
    }
    return render(request, 'oms/order_form.html', context)

def update_order_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        notes = request.POST.get('notes', '')
        items_data = request.POST.get('items_data')
        
        try:
            with transaction.atomic():
                vendor = get_object_or_404(Vendor, id=vendor_id)
                order.vendor = vendor
                order.notes = notes
                order.save()
                
                # Delete existing items and recreate them
                order.items.all().delete()
                
                if items_data:
                    items = json.loads(items_data)
                    for item in items:
                        product = get_object_or_404(Product, id=item['product_id'])
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=int(item['quantity']),
                            unit_price=float(item['unit_price']),
                            discount_type=item['discount_type'],
                            discount_value=float(item['discount_value'])
                        )
                
                messages.success(request, f'Order {order.pk} updated successfully!')
                return redirect('order-detail', pk=order.pk)
                
        except Exception as e:
            messages.error(request, f'Error updating order: {str(e)}')
    
    vendors = Vendor.objects.all()
    products = Product.objects.filter(is_active=True)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'vendors': vendors,
        'products': products,
        'order_items': order_items,
    }
    return render(request, 'oms/order_form.html', context)

class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'oms/order_confirm_delete.html'
    success_url = reverse_lazy('order-list')

def get_product_price(request):
    """AJAX view to get product price"""
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            return JsonResponse({
                'success': True,
                'price': float(product.mrp),
                'name': product.item_name
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid product ID'})

def generate_invoice(request, pk):
    """Generate invoice for an order"""
    order = get_object_or_404(Order, pk=pk)
    
    context = {
        'order': order,
    }
    
    return render(request, 'oms/invoice.html', context)