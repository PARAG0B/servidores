from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Movimientos
    path("movements/", views.movement_list, name="movement_list"),
    path("movements/new/", views.movement_create, name="movement_create"),
    path("movements/export/", views.movement_export_csv, name="movement_export_csv"),

    # Productos (historial por producto)
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/new/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),

    # Historial por producto
    path("products/<int:pk>/history/", views.product_history, name="product_history"),


]


