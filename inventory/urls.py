from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("movements/", views.movement_list, name="movement_list"),
    path("movements/new/", views.movement_create, name="movement_create"),
    path("movements/<int:pk>/", views.movement_detail, name="movement_detail"),
    path("movements/<int:pk>/edit/", views.movement_update, name="movement_update"),
    path("movements/<int:pk>/delete/", views.movement_delete, name="movement_delete"),
    path("movements/export/", views.movement_export_csv, name="movement_export_csv"),

    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
]


