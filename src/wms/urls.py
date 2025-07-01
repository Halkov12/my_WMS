from django.urls import path

from wms.views import (ChangeLogReportView, DashboardView, IndexView,
                       IssueView, ProductCreateView, ProductListView,
                       ProductReportView, ProductUpdateView, ProductDeleteView, ReceiptView,
                       ReportListView, StockOperationReportView, WriteOffView,
                       ToolsView, barcode_generator, export_products_excel, export_products_csv, import_products, preview_import_products, preview_import_products_ajax, backup_products, restore_products, backup_all_data, restore_all_data, HelpView, HelpProductsView, HelpOperationsView, HelpReportsView, HelpToolsView, HelpFaqView, BarcodeGeneratorView, send_email_to_managers)

app_name = "wms"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("receipt/create/", ReceiptView.as_view(), name="receipt_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("reports/", ReportListView.as_view(), name="report_list"),
    path("reports/products/", ProductReportView.as_view(), name="product_report"),
    path("reports/stock-operations/", StockOperationReportView.as_view(), name="stock_report"),
    path("reports/change-logs/", ChangeLogReportView.as_view(), name="changelog_report"),
    path("issue/", IssueView.as_view(), name="issue_list"),
    path("writeoff/", WriteOffView.as_view(), name="writeoff_list"),
    path("tools/", ToolsView.as_view(), name="tools"),
    path("barcode-generator/", BarcodeGeneratorView.as_view(), name="barcode_generator_page"),
    path("tools/barcode/", barcode_generator, name="barcode_generator"),
    path("tools/export/excel/", export_products_excel, name="export_products_excel"),
    path("tools/export/csv/", export_products_csv, name="export_products_csv"),
    path("tools/import/", import_products, name="import_products"),
    path("tools/import/preview/", preview_import_products, name="preview_import_products"),
    path("tools/import/preview-ajax/", preview_import_products_ajax, name="preview_import_products_ajax"),
    path("tools/backup/", backup_products, name="backup_products"),
    path("tools/restore/", restore_products, name="restore_products"),
    path("tools/backup-all/", backup_all_data, name="backup_all_data"),
    path("tools/restore-all/", restore_all_data, name="restore_all_data"),
    path("tools/send-email/", send_email_to_managers, name="send_email"),
    path("help/", HelpView.as_view(), name="help_main"),
    path("help/products/", HelpProductsView.as_view(), name="help_products"),
    path("help/operations/", HelpOperationsView.as_view(), name="help_operations"),
    path("help/reports/", HelpReportsView.as_view(), name="help_reports"),
    path("help/tools/", HelpToolsView.as_view(), name="help_tools"),
    path("help/faq/", HelpFaqView.as_view(), name="help_faq"),
]