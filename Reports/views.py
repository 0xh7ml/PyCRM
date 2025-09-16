from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

from OMS.models import Order, OrderItem
from Inventory.models import Stock, StockIn, StockInItem
from Product.models import Product
from CRM.models import Vendor


class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Quick stats for the dashboard
        context['total_orders'] = Order.objects.count()
        context['total_order_value'] = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        context['total_products'] = Product.objects.filter(is_active=True).count()
        context['low_stock_items'] = Stock.objects.filter(quantity__lt=10).count()
        
        return context


class SalesReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/sales_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date filters from GET parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        vendor_id = self.request.GET.get('vendor')
        
        # Base queryset
        orders = Order.objects.all()
        
        # Apply filters
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date__gte=start_date)
                context['start_date'] = start_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date__lte=end_date)
                context['end_date'] = end_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
                
        if vendor_id:
            orders = orders.filter(vendor_id=vendor_id)
            context['selected_vendor'] = vendor_id
        
        # Calculate sales metrics
        sales_summary = orders.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount'),
            average_order_value=Avg('total_amount')
        )
        
        # Top selling products
        top_products = OrderItem.objects.filter(
            order__in=orders
        ).values(
            'product__item_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price') - F('discount_value'))
        ).order_by('-total_revenue')[:10]
        
        # Sales by vendor
        vendor_sales = orders.values(
            'vendor__name'
        ).annotate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('-total_revenue')
        
        # Monthly sales trend (last 12 months)
        today = timezone.now().date()
        twelve_months_ago = today - timedelta(days=365)
        
        monthly_sales = []
        for i in range(12):
            month_start = (today.replace(day=1) - timedelta(days=32*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_orders = Order.objects.filter(
                created_at__date__gte=month_start,
                created_at__date__lte=month_end
            )
            
            monthly_data = month_orders.aggregate(
                total_orders=Count('id'),
                total_revenue=Sum('total_amount')
            )
            
            monthly_sales.append({
                'month': month_start.strftime('%B %Y'),
                'orders': monthly_data['total_orders'] or 0,
                'revenue': float(monthly_data['total_revenue'] or 0)
            })
        
        monthly_sales.reverse()  # Show oldest to newest
        
        context.update({
            'orders': orders.order_by('-created_at')[:50],  # Latest 50 orders
            'sales_summary': sales_summary,
            'top_products': top_products,
            'vendor_sales': vendor_sales,
            'monthly_sales': json.dumps(monthly_sales),  # Serialize for JavaScript
            'vendors': Vendor.objects.all(),
        })
        
        return context


class StockReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/stock_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filters
        low_stock_threshold = int(self.request.GET.get('low_stock_threshold', 10))
        category_filter = self.request.GET.get('category')
        
        # Base stock queryset
        stocks = Stock.objects.select_related('product').all()
        
        # Stock summary
        stock_summary = {
            'total_products': stocks.count(),
            'total_stock_value': 0,
            'low_stock_items': stocks.filter(quantity__lt=low_stock_threshold).count(),
            'out_of_stock_items': stocks.filter(quantity=0).count(),
        }
        
        # Calculate total stock value
        total_value = 0
        for stock in stocks:
            total_value += stock.quantity * float(stock.product.purchase_price)
        stock_summary['total_stock_value'] = total_value
        
        # Current stock levels
        current_stock = stocks.annotate(
            stock_value=F('quantity') * F('product__purchase_price')
        ).order_by('quantity')
        
        # Low stock items
        low_stock_items = stocks.filter(
            quantity__lt=low_stock_threshold,
            quantity__gt=0
        ).order_by('quantity')
        
        # Out of stock items
        out_of_stock_items = stocks.filter(quantity=0)
        
        # Recent stock movements (from StockIn)
        recent_stock_ins = StockIn.objects.filter(
            is_completed=True
        ).order_by('-created_at')[:20]
        
        # Stock in summary by product (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_stock_movements = StockInItem.objects.filter(
            stock_in__created_at__gte=thirty_days_ago,
            stock_in__is_completed=True
        ).values(
            'product__item_name'
        ).annotate(
            total_added=Sum('quantity'),
            transactions=Count('id')
        ).order_by('-total_added')[:10]
        
        # Products with highest turnover (most ordered)
        high_turnover_products = OrderItem.objects.filter(
            order__created_at__gte=thirty_days_ago
        ).values(
            'product__item_name'
        ).annotate(
            total_sold=Sum('quantity'),
            orders_count=Count('order', distinct=True)
        ).order_by('-total_sold')[:10]
        
        context.update({
            'stock_summary': stock_summary,
            'current_stock': current_stock,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'recent_stock_ins': recent_stock_ins,
            'recent_stock_movements': recent_stock_movements,
            'high_turnover_products': high_turnover_products,
            'low_stock_threshold': low_stock_threshold,
        })
        
        return context


@login_required
def export_sales_report(request):
    """Export sales report as CSV"""
    # Get same filters as the view
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    vendor_id = request.GET.get('vendor')
    
    orders = Order.objects.all()
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=start_date)
        except ValueError:
            pass
            
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=end_date)
        except ValueError:
            pass
            
    if vendor_id:
        orders = orders.filter(vendor_id=vendor_id)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Order ID', 'Date', 'Vendor', 'Total Amount', 'Items Count', 'Notes'
    ])
    
    for order in orders.select_related('vendor'):
        writer.writerow([
            order.pk,
            order.created_at.strftime('%Y-%m-%d %H:%M'),
            order.vendor.name,
            order.total_amount,
            order.items.count(),
            order.notes or ''
        ])
    
    return response


@login_required
def export_stock_report(request):
    """Export stock report as CSV"""
    low_stock_threshold = int(request.GET.get('low_stock_threshold', 10))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Product Name', 'Current Quantity', 'Reserved Quantity', 
        'Available Quantity', 'Purchase Price', 'MRP', 'Stock Value', 'Status'
    ])
    
    stocks = Stock.objects.select_related('product').all()
    
    for stock in stocks:
        status = 'Out of Stock' if stock.quantity == 0 else \
                 'Low Stock' if stock.quantity < low_stock_threshold else 'In Stock'
        
        stock_value = stock.quantity * float(stock.product.purchase_price)
        
        writer.writerow([
            stock.product.item_name,
            stock.quantity,
            stock.reserved_quantity,
            stock.available_quantity,
            stock.product.purchase_price,
            stock.product.mrp,
            f'{stock_value:.2f}',
            status
        ])
    
    return response
