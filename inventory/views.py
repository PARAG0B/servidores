import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MovementForm, ProductForm
from .models import Movement, Product, Stock


@login_required
def dashboard(request):
    # Totales por producto
    totals = (
        Stock.objects
        .select_related("product")
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
    }
    return render(request, "inventory/dashboard.html", context)


@login_required
def movement_list(request):
    movements = (
        Movement.objects
        .select_related("warehouse", "product")
        .order_by("-id")[:100]
    )
    return render(request, "inventory/movement_list.html", {"movements": movements})


@login_required
def movement_create(request):
    if request.method == "POST":
        form = MovementForm(request.POST)
        if form.is_valid():
            try:
                # Aquí se ejecuta Movement.save() con la lógica de stock
                form.save()
            except ValidationError as e:
                form.add_error(None, e.message)
            else:
                messages.success(request, "Movimiento registrado correctamente.")
                return redirect("inventory:movement_list")
    else:
        form = MovementForm()

    return render(request, "inventory/movement_form.html", {"form": form})


@login_required
def movement_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="movimientos_inventrack.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "ID",
        "Fecha / Hora",
        "Tipo",
        "Bodega",
        "Producto",
        "Cantidad",
        "Referencia",
        "Notas",
    ])

    movements = (
        Movement.objects
        .select_related("warehouse", "product")
        .order_by("-id")
    )

    for m in movements:
        writer.writerow([
            m.id,
            m.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(m, "created_at") and m.created_at else "",
            getattr(m, "get_movement_type_display", lambda: m.movement_type)(),
            str(m.warehouse),
            str(m.product),
            m.quantity,
            m.reference or "",
            (m.notes or "").replace("\n", " "),
        ])

    return response


@login_required
def product_list(request):
    products = Product.objects.all().order_by("name")
    context = {
        "products": products,
    }
    return render(request, "inventory/product_list.html", context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    movements = (
        Movement.objects
        .filter(product=product)
        .select_related("warehouse")
        .order_by("-id")
    )

    context = {
        "product": product,
        "movements": movements,
    }
    return render(request, "inventory/product_detail.html", context)



@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "inventory/product_form.html", {"form": form, "title": "Nuevo producto"})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Editar producto"})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "inventory/product_confirm_delete.html", {"product": product})


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
