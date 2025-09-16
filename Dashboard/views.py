from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """
    Dashboard view with info cards for quick access to different apps
    """
    # Info cards data for each app module
    info_cards = [
        {
            'title': 'CRM',
            'description': 'Customer Relationship Management',
            'icon': 'fas fa-users',
            'color': 'info',
            'links': [
                {'name': 'Vendors', 'url': 'vendor-list'},
                {'name': 'Add Vendor', 'url': 'vendor-create'},
            ]
        },
        {
            'title': 'Products',
            'description': 'Product Management System',
            'icon': 'fas fa-box',
            'color': 'success',
            'links': [
                {'name': 'Products', 'url': 'product:product_list'},
                {'name': 'Categories', 'url': 'product:category_list'},
                {'name': 'Attributes', 'url': 'product:attribute_list'},
            ]
        },
        {
            'title': 'Orders',
            'description': 'Order Management System',
            'icon': 'fas fa-shopping-cart',
            'color': 'warning',
            'links': [
                {'name': 'All Orders', 'url': 'order-list'},
                {'name': 'Create Order', 'url': 'order-create'},
            ]
        },
        {
            'title': 'Inventory',
            'description': 'Stock Management System',
            'icon': 'fas fa-warehouse',
            'color': 'primary',
            'links': [
                {'name': 'Stock In', 'url': 'stock-in-list'},
                {'name': 'New Stock In', 'url': 'stock-in-create'},
                {'name': 'Stock Levels', 'url': 'stock-list'},
            ]
        },
        {
            'title': 'HRM',
            'description': 'Human Resource Management',
            'icon': 'fas fa-user-tie',
            'color': 'secondary',
            'links': [
                {'name': 'Employees', 'url': '#'},
                {'name': 'Add Employee', 'url': '#'},
            ]
        },
        {
            'title': 'Reports',
            'description': 'Reports & Analytics',
            'icon': 'fas fa-chart-bar',
            'color': 'danger',
            'links': [
                {'name': 'Reports Dashboard', 'url': 'reports-dashboard'},
                {'name': 'Sales Report', 'url': 'sales-report'},
                {'name': 'Stock Report', 'url': 'stock-report'},
            ]
        },
    ]
    
    context = {
        'info_cards': info_cards,
    }
    return render(request, 'dashboard/dashboard.html', context)
