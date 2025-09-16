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
from Inventory.models import Stock
import json

def check_stock_availability(product_id, requested_quantity):
    """
    Check if a product has enough stock available for the requested quantity.
    Returns (is_available, available_quantity, error_message)
    """
    try:
        product = Product.objects.get(id=product_id)
        try:
            stock = Stock.objects.get(product=product)
            available_qty = stock.available_quantity
            
            if available_qty >= requested_quantity:
                return True, available_qty, None
            else:
                error_msg = f"Not enough stock for '{product.item_name}'. Available: {available_qty}, Requested: {requested_quantity}"
                return False, available_qty, error_msg
        except Stock.DoesNotExist:
            error_msg = f"No stock record found for product '{product.item_name}'"
            return False, 0, error_msg
    except Product.DoesNotExist:
        error_msg = f"Product with ID {product_id} not found"
        return False, 0, error_msg

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
            items = json.loads(items_data)
            print(f"Items data parsed: {items}")
            
            # Validate stock for all items before creating order
            stock_errors = []
            for item_data in items:
                product_id = item_data['product_id']
                quantity = int(item_data['quantity'])
                
                is_available, available_qty, error_msg = check_stock_availability(product_id, quantity)
                if not is_available:
                    stock_errors.append(error_msg)
            
            if stock_errors:
                for error in stock_errors:
                    messages.error(request, error)
                vendors = Vendor.objects.all()
                products = Product.objects.filter(is_active=True)
                return render(request, 'oms/order_form.html', {'vendors': vendors, 'products': products})
            
            # All stock checks passed, create the order
            with transaction.atomic():
                vendor = get_object_or_404(Vendor, id=vendor_id)
                order = Order.objects.create(vendor=vendor, notes=notes)
                print(f"Order created with ID: {order.pk}")
                
                # Track items created for potential rollback
                created_items = []
                stock_reductions = []
                
                try:
                    for item_data in items:
                        product = get_object_or_404(Product, id=item_data['product_id'])
                        quantity = int(item_data['quantity'])
                        
                        # Double-check stock availability just before reducing
                        try:
                            stock = Stock.objects.select_for_update().get(product=product)
                            if not stock.can_fulfill(quantity):
                                raise ValueError(f"Insufficient stock for {product.item_name}. Available: {stock.available_quantity}, Requested: {quantity}")
                        except Stock.DoesNotExist:
                            raise ValueError(f"No stock record found for product {product.item_name}")
                        
                        # Create order item
                        order_item = OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=float(item_data['unit_price']),
                            discount_type=item_data['discount_type'],
                            discount_value=float(item_data['discount_value'])
                        )
                        created_items.append(order_item)
                        print(f"OrderItem created: {order_item}")
                        
                        # Reduce stock quantity after successful order item creation
                        if stock.reduce_stock(quantity):
                            stock_reductions.append((stock, quantity))
                            print(f"Stock reduced for {product.item_name}: -{quantity} (New quantity: {stock.quantity})")
                        else:
                            raise ValueError(f"Failed to reduce stock for {product.item_name}")
                    
                    # Recalculate total
                    order.calculate_total()
                    print(f"Order total calculated: {order.total_amount}")
                    
                    messages.success(request, f'Order {order.pk} created successfully!')
                    return redirect('order-detail', pk=order.pk)
                    
                except Exception as e:
                    # If anything goes wrong, the transaction will rollback automatically
                    print(f"Error during order creation: {e}")
                    raise e
                
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
            # Validate stock for all items before updating order
            if items_data:
                items = json.loads(items_data)
                stock_errors = []
                
                for item_data in items:
                    product_id = item_data['product_id']
                    quantity = int(item_data['quantity'])
                    
                    is_available, available_qty, error_msg = check_stock_availability(product_id, quantity)
                    if not is_available:
                        stock_errors.append(error_msg)
                
                if stock_errors:
                    for error in stock_errors:
                        messages.error(request, error)
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
            
            # All stock checks passed, update the order
            with transaction.atomic():
                vendor = get_object_or_404(Vendor, id=vendor_id)
                order.vendor = vendor
                order.notes = notes
                order.save()
                
                # Store existing items for stock restoration before deletion
                old_items = []
                for old_item in order.items.all():
                    old_items.append({
                        'product': old_item.product,
                        'quantity': old_item.quantity
                    })
                
                # Restore stock for old items
                for old_item_data in old_items:
                    try:
                        stock = Stock.objects.select_for_update().get(product=old_item_data['product'])
                        stock.add_stock(old_item_data['quantity'])
                        print(f"Stock restored for {old_item_data['product'].item_name}: +{old_item_data['quantity']} (New quantity: {stock.quantity})")
                    except Stock.DoesNotExist:
                        print(f"Warning: No stock record found for product {old_item_data['product'].item_name}")
                        # Create stock record with the restored quantity
                        Stock.objects.create(product=old_item_data['product'], quantity=old_item_data['quantity'])
                
                # Delete existing items
                order.items.all().delete()
                
                # Create new items and reduce stock
                if items_data:
                    items = json.loads(items_data)
                    for item in items:
                        product = get_object_or_404(Product, id=item['product_id'])
                        quantity = int(item['quantity'])
                        
                        # Double-check stock availability
                        try:
                            stock = Stock.objects.select_for_update().get(product=product)
                            if not stock.can_fulfill(quantity):
                                raise ValueError(f"Insufficient stock for {product.item_name}. Available: {stock.available_quantity}, Requested: {quantity}")
                        except Stock.DoesNotExist:
                            raise ValueError(f"No stock record found for product {product.item_name}")
                        
                        # Create new order item
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=float(item['unit_price']),
                            discount_type=item['discount_type'],
                            discount_value=float(item['discount_value'])
                        )
                        
                        # Reduce stock for new items
                        if stock.reduce_stock(quantity):
                            print(f"Stock reduced for {product.item_name}: -{quantity} (New quantity: {stock.quantity})")
                        else:
                            raise ValueError(f"Failed to reduce stock for {product.item_name}")
                
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
    
    def delete(self, request, *args, **kwargs):
        """Override delete to restore stock when order is deleted"""
        order = self.get_object()
        
        # Restore stock for all order items before deletion
        order.restore_stock()
        
        # Delete the order (which will also delete order items due to CASCADE)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Order {order.pk} deleted successfully and stock restored.')
        return response

def get_product_price(request):
    """AJAX view to get product price and stock info"""
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity', 1)
    
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            
            # Check stock availability
            is_available, available_qty, error_msg = check_stock_availability(product_id, int(quantity))
            
            return JsonResponse({
                'success': True,
                'price': float(product.mrp),
                'name': product.item_name,
                'stock_available': is_available,
                'available_quantity': available_qty,
                'stock_message': error_msg if not is_available else f"Available: {available_qty}"
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid quantity format'})
    
    return JsonResponse({'success': False, 'error': 'Invalid product ID'})

def check_stock_ajax(request):
    """AJAX view to check stock availability"""
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity', 1)
    
    if product_id and quantity:
        try:
            is_available, available_qty, error_msg = check_stock_availability(product_id, int(quantity))
            
            return JsonResponse({
                'success': True,
                'stock_available': is_available,
                'available_quantity': available_qty,
                'message': error_msg if not is_available else f"Stock available: {available_qty}"
            })
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid quantity format'})
    
    return JsonResponse({'success': False, 'error': 'Missing product ID or quantity'})

def generate_invoice(request, pk):
    """Generate invoice for an order"""
    order = get_object_or_404(Order, pk=pk)
    
    context = {
        'order': order,
    }
    
    return render(request, 'oms/invoice.html', context)