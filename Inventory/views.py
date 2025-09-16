from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import StockIn, StockInItem, Stock
from Product.models import Product
import json
import logging

logger = logging.getLogger(__name__)


def stock_in_list(request):
    """List all stock in records with search and pagination"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    stock_ins = StockIn.objects.all()
    
    if query:
        stock_ins = stock_ins.filter(
            Q(stock_in_id__icontains=query) |
            Q(notes__icontains=query)
        )
    
    if status_filter == 'completed':
        stock_ins = stock_ins.filter(is_completed=True)
    elif status_filter == 'pending':
        stock_ins = stock_ins.filter(is_completed=False)
    
    paginator = Paginator(stock_ins, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'inventory/stock_in_list.html', context)


def stock_in_detail(request, pk):
    """View stock in details"""
    stock_in = get_object_or_404(StockIn, pk=pk)
    items = stock_in.items.all().select_related('product')
    
    context = {
        'stock_in': stock_in,
        'items': items,
    }
    return render(request, 'inventory/stock_in_detail.html', context)


def stock_in_create(request):
    """Create new stock in record"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Parse JSON data from form
                items_data = json.loads(request.POST.get('items_data', '[]'))
                notes = request.POST.get('notes', '')
                
                if not items_data:
                    messages.error(request, 'Please add at least one product to create stock in.')
                    return redirect('stock-in-create')
                
                # Create stock in record
                stock_in = StockIn.objects.create(
                    notes=notes
                )
                
                # Create stock in items
                for item_data in items_data:
                    product_id = item_data.get('product_id')
                    quantity = int(item_data.get('quantity', 0))
                    
                    if quantity <= 0:
                        continue
                    
                    try:
                        product = Product.objects.get(id=product_id)
                        StockInItem.objects.create(
                            stock_in=stock_in,
                            product=product,
                            quantity=quantity
                        )
                    except Product.DoesNotExist:
                        logger.warning(f"Product {product_id} not found while creating stock in")
                        continue
                
                stock_in.calculate_total_items()
                
                messages.success(request, f'Stock In {stock_in.stock_in_id} created successfully!')
                return redirect('stock-in-detail', pk=stock_in.pk)
                
        except Exception as e:
            logger.error(f"Error creating stock in: {str(e)}")
            messages.error(request, f'Error creating stock in: {str(e)}')
    
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'inventory/stock_in_form.html', context)


def stock_in_edit(request, pk):
    """Edit existing stock in record (only if not completed)"""
    stock_in = get_object_or_404(StockIn, pk=pk)
    
    if stock_in.is_completed:
        messages.warning(request, 'Cannot edit completed stock in records.')
        return redirect('stock-in-detail', pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Parse JSON data from form
                items_data = json.loads(request.POST.get('items_data', '[]'))
                notes = request.POST.get('notes', '')
                
                if not items_data:
                    messages.error(request, 'Please add at least one product to update stock in.')
                    return redirect('stock-in-edit', pk=pk)
                
                # Update stock in notes
                stock_in.notes = notes
                stock_in.save()
                
                # Clear existing items and create new ones
                stock_in.items.all().delete()
                
                for item_data in items_data:
                    product_id = item_data.get('product_id')
                    quantity = int(item_data.get('quantity', 0))
                    
                    if quantity <= 0:
                        continue
                    
                    try:
                        product = Product.objects.get(id=product_id)
                        StockInItem.objects.create(
                            stock_in=stock_in,
                            product=product,
                            quantity=quantity
                        )
                    except Product.DoesNotExist:
                        logger.warning(f"Product {product_id} not found while updating stock in")
                        continue
                
                stock_in.calculate_total_items()
                
                messages.success(request, f'Stock In {stock_in.stock_in_id} updated successfully!')
                return redirect('stock-in-detail', pk=stock_in.pk)
                
        except Exception as e:
            logger.error(f"Error updating stock in: {str(e)}")
            messages.error(request, f'Error updating stock in: {str(e)}')
    
    # Get existing items for editing
    existing_items = []
    for item in stock_in.items.all():
        existing_items.append({
            'product_id': item.product.id,
            'product_name': item.product.item_name,
            'product_barcode': item.product.barcode,
            'quantity': item.quantity
        })
    
    products = Product.objects.all()
    context = {
        'stock_in': stock_in,
        'products': products,
        'existing_items': json.dumps(existing_items),
    }
    return render(request, 'inventory/stock_in_form.html', context)


def stock_in_complete(request, pk):
    """Complete a stock in and update product stocks"""
    stock_in = get_object_or_404(StockIn, pk=pk)
    
    if stock_in.is_completed:
        messages.warning(request, 'Stock in is already completed.')
        return redirect('stock-in-detail', pk=pk)
    
    if request.method == 'POST':
        if stock_in.complete_stock_in():
            messages.success(request, f'Stock In {stock_in.stock_in_id} completed successfully! Product stocks updated.')
        else:
            messages.error(request, 'Failed to complete stock in.')
    
    return redirect('stock-in-detail', pk=pk)


def stock_in_delete(request, pk):
    """Delete stock in record (only if not completed)"""
    stock_in = get_object_or_404(StockIn, pk=pk)
    
    if stock_in.is_completed:
        messages.warning(request, 'Cannot delete completed stock in records.')
        return redirect('stock-in-detail', pk=pk)
    
    if request.method == 'POST':
        stock_in_id = stock_in.stock_in_id
        stock_in.delete()
        messages.success(request, f'Stock In {stock_in_id} deleted successfully!')
        return redirect('stock-in-list')
    
    context = {
        'stock_in': stock_in,
    }
    return render(request, 'inventory/stock_in_confirm_delete.html', context)

# AJAX Views for barcode and product search

@require_http_methods(["GET"])
def search_product_by_barcode(request):
    """AJAX endpoint to search product by barcode"""
    barcode = request.GET.get('barcode', '').strip()
    
    if not barcode:
        return JsonResponse({'error': 'Barcode parameter is required'}, status=400)
    
    try:
        product = Product.objects.get(barcode=barcode)
        
        # Get current stock quantity
        try:
            stock = Stock.objects.get(product=product)
            current_stock = stock.quantity
        except Stock.DoesNotExist:
            current_stock = 0
        
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.item_name,
                'barcode': product.barcode,
                'purchase_price': str(product.purchase_price),
                'mrp': str(product.mrp),
                'current_stock': current_stock,
                'description': product.description or ''
            }
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Product with barcode "{barcode}" not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error searching product by barcode: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
@login_required
def search_products(request):
    """AJAX endpoint to search products by name or barcode"""
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 10)), 50)  # Max 50 results
    
    if not query or len(query) < 2:
        return JsonResponse({'products': []})
    
    try:
        products = Product.objects.filter(
            Q(item_name__icontains=query) |
            Q(barcode__icontains=query)
        )[:limit]
        
        products_data = []
        for product in products:
            # Get current stock quantity
            try:
                stock = Stock.objects.get(product=product)
                current_stock = stock.quantity
            except Stock.DoesNotExist:
                current_stock = 0
            
            products_data.append({
                'id': product.id,
                'name': product.item_name,
                'barcode': product.barcode,
                'purchase_price': str(product.purchase_price),
                'mrp': str(product.mrp),
                'current_stock': current_stock,
                'description': product.description or ''
            })
        
        return JsonResponse({
            'success': True,
            'products': products_data
        })
        
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


def stock_list(request):
    """List all product stocks with search"""
    query = request.GET.get('q', '')
    low_stock = request.GET.get('low_stock', '')
    
    stocks = Stock.objects.select_related('product').all()
    
    if query:
        stocks = stocks.filter(
            Q(product__item_name__icontains=query) |
            Q(product__barcode__icontains=query)
        )
    
    if low_stock == '1':
        # Show products with stock less than 10
        stocks = stocks.filter(quantity__lt=10)
    elif low_stock == '0':
        # Show out of stock products
        stocks = stocks.filter(quantity=0)
    
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'low_stock': low_stock,
    }
    return render(request, 'inventory/stock_list.html', context)
