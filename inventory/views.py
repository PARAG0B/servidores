from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Sum

import io
import qrcode
from django.urls import reverse

from .models import Product, Stock, Movement
from .forms import ProductForm, MovementForm
import csv




@login_required
def dashboard(request):
    # Totales por producto (solo usamos nombre, nada raro)
    totals = (
        Stock.objects
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("product__name")
    )

    # Detalle por bodega
    stocks = (
        Stock.objects
        .select_related("warehouse", "product")
        .order_by("warehouse__name", "product__name")
    )

    context = {
        "totals": totals,
        "stocks": stocks,
        # Nada más, así el template no depende de low_stock ni cosas nuevas
    }

    return render(request, "inventory/dashboard.html", context)

@login_required
def movement_list(request):
    movements = Movement.objects.select_related(
        "product"
    ).order_by("-created_at")
    return render(
        request,
        "inventory/movement_list.html",
        {"movements": movements},
    )


@login_required
@transaction.atomic
def movement_create(request):
    if request.method == "POST":
        form = MovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            # Si tu modelo tiene campo user, lo rellenamos
            if hasattr(movement, "user") and request.user.is_authenticated:
                movement.user = request.user
            movement.save()
            messages.success(request, "Movimiento registrado correctamente.")
            return redirect("movement_list")
    else:
        form = MovementForm()

    return render(
        request,
        "inventory/movement_form.html",
        {"form": form, "title": "Nuevo movimiento"},
    )


@login_required
def movement_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="movements.csv"'

    writer = csv.writer(response)

    # Cabeceras dinámicas basadas en los campos del modelo
    field_names = [f.name for f in Movement._meta.fields]
    writer.writerow(field_names)

    for m in Movement.objects.all():
        row = [getattr(m, f) for f in field_names]
        writer.writerow(row)

    return response


@login_required
def export_movements_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="inventrack_movements.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Fecha",
        "Producto",
        "Tipo",
        "Cantidad",
        "Bodega origen",
        "Bodega destino",
        "Usuario",
    ])

    movements = (
        Movement.objects
        .select_related("product", "warehouse_from", "warehouse_to", "user")
        .order_by("-id")   # más seguro que asumir created_at
    )

    for m in movements:
        # Fecha: intentamos usar created_at, si no existe usamos created
        created_value = getattr(m, "created_at", None)
        if created_value is None:
            created_value = getattr(m, "created", None)
        if created_value is not None:
            created_str = created_value.strftime("%Y-%m-%d %H:%M")
        else:
            created_str = ""

        # Tipo legible si existe get_movement_type_display
        if hasattr(m, "get_movement_type_display"):
            movement_type = m.get_movement_type_display()
        else:
            movement_type = getattr(m, "movement_type", "")

        writer.writerow([
            created_str,
            m.product.name if getattr(m, "product_id", None) else "",
            movement_type,
            m.quantity,
            m.warehouse_from.name if getattr(m, "warehouse_from_id", None) else "",
            m.warehouse_to.name if getattr(m, "warehouse_to_id", None) else "",
            m.user.username if getattr(m, "user_id", None) else "",
        ])

    return response

@login_required
def export_products_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)

    field_names = [f.name for f in Product._meta.fields]
    writer.writerow(field_names)

    for p in Product.objects.all():
        writer.writerow([getattr(p, f) for f in field_names])

    return response


@login_required
def product_list(request):
    products = Product.objects.all()

    # Campos dinámicos del modelo, para no adivinar nombres
    field_names = [f.name for f in Product._meta.fields]

    rows = []
    for p in products:
        rows.append([getattr(p, f) for f in field_names])

    context = {
        "field_names": field_names,
        "rows": rows,
    }
    return render(request, "inventory/product_list.html", context)


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(
        request,
        "inventory/product_form.html",
        {"form": form, "title": "Nuevo producto"},
    )


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "inventory/product_form.html",
        {"form": form, "title": "Editar producto"},
    )


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("product_list")

    return render(
        request,
        "inventory/product_confirm_delete.html",
        {"product": product},
    )


@login_required
def product_history(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = (
        Movement.objects
        .select_related("warehouse", "user")
        .filter(product=product)
        .order_by("-created_at")
    )
    return render(
        request,
        "inventory/product_history.html",
        {"product": product, "movements": movements},
    )


@login_required
def export_movements_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="movements.csv"'
    writer = csv.writer(response)

    field_names = [f.name for f in Movement._meta.fields]
    writer.writerow(field_names)

    for m in Movement.objects.all():
        writer.writerow([getattr(m, f) for f in field_names])

    return response


