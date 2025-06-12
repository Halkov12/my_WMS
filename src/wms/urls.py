from django.urls import path

from wms.views import (ChangeLogReportView, DashboardView, IndexView,
                       IssueView, ProductCreateView, ProductListView,
                       ProductReportView, ProductUpdateView, ReceiptView,
                       ReportListView, StockOperationReportView)

app_name = "wms"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("receipt/create/", ReceiptView.as_view(), name="receipt_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("reports/", ReportListView.as_view(), name="report_list"),
    path("reports/products/", ProductReportView.as_view(), name="product_report"),
    path("reports/stock-operations/", StockOperationReportView.as_view(), name="stock_report"),
    path("reports/change-logs/", ChangeLogReportView.as_view(), name="changelog_report"),
    path("issue/", IssueView.as_view(), name="issue_list"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_edit"),
]
