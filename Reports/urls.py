from django.urls import path
from .views import (
    ReportsDashboardView, 
    SalesReportView, 
    StockReportView,
    export_sales_report,
    export_stock_report
)

urlpatterns = [
    path('', ReportsDashboardView.as_view(), name='reports-dashboard'),
    path('sales/', SalesReportView.as_view(), name='sales-report'),
    path('stock/', StockReportView.as_view(), name='stock-report'),
    path('sales/export/', export_sales_report, name='export-sales-report'),
    path('stock/export/', export_stock_report, name='export-stock-report'),
]