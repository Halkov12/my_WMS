from django.urls import path

from wms.views import (DashboardView, IndexView, ProductCreateView,
                       ProductListView, ReceiptView, ReportListView, ProductReportView, StockOperationReportView,
                       ChangeLogReportView)

app_name = "wms"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("receipt/create/", ReceiptView.as_view(), name="receipt_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path('reports/', ReportListView.as_view(), name='report_list'),
    path('reports/products/', ProductReportView.as_view(), name='product_report'),
    path('reports/stock-operations/', StockOperationReportView.as_view(), name='stock_report'),
    path('reports/change-logs/', ChangeLogReportView.as_view(), name='changelog_report'),
]
