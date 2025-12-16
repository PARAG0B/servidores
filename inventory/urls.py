
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Productos
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("products/<int:pk>/history/", views.product_history, name="product_history"),
    path("products/export/csv/", views.export_products_csv, name="product_export"),

    # Movimientos
    path("movements/", views.movement_list, name="movement_list"),
    path("movements/create/", views.movement_create, name="movement_create"),
    path("products/export/csv/", views.export_products_csv, name=" export_movements_csv"),
    path("movements/new/", views.movement_create, name="movement_create"),
]
