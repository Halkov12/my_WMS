from django.urls import path

from wms.views import index, dashboard_view, product_list_view

app_name = "wms"

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path('products/', product_list_view, name='product_list'),
]
