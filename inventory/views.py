from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import csv

from .models import Stock, Movement, Product
from .forms import MovementForm, ProductForm

@login_required
def dashboard(request):
    # Totales por producto
    totals = (
        Stock.objects
        .values("product__name", "product__code")
        .annotate(total=Sum("quantity"))
        .order_by("product__name")
    )

    # Detalle por bodega
    stocks = (
        Stock.objects
        .select_related("warehouse", "product")
        .order_by("warehouse__name", "product__name")
    )

    # Productos con stock total por debajo del mínimo
    low_stock = (
        Stock.objects
        .values("product__id", "product__name", "product__code", "product__min_stock")
        .annotate(total=Sum("quantity"))
        .filter(
            product__min_stock__isnull=False,
            product__min_stock__gt=0,
            total__lt=F("product__min_stock"),
        )
        .order_by("product__name")
    )

    context = {
        "totals": totals,
        "stocks": stocks,
        "low_stock": low_stock,
        "low_stock_count": low_stock.count(),
    }
    return render(request, "inventory/dashboard.html", context)

@login_required
def movement_list(request):
    # Ahora sí, leemos de la base de datos
    movements = Movement.objects.all()

    context = {
        "movements": movements,
    }
    return render(request, "inventory/movement_list.html", context)

@login_required
def movement_create(request):
    if request.method == "POST":
        form = MovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.user = request.user
            movement.save()   # aquí se actualiza el stock
            return redirect("movement_list")
    else:
        form = MovementForm()
    return render(request, "inventory/movement_form.html", {"form": form})

@login_required
def export_products_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="inventrack_products.csv"'

    writer = csv.writer(response)
    writer.writerow(["Código", "Nombre", "Stock mínimo", "Activo", "Stock total"])

    products = Product.objects.all().order_by("name")
    totals = (
        Stock.objects.values("product_id")
        .annotate(total=Sum("quantity"))
    )
    totals_by_product = {row["product_id"]: row["total"] for row in totals}

    for p in products:
        total_stock = totals_by_product.get(p.id, 0)
        writer.writerow([
            p.code,
            p.name,
            getattr(p, "min_stock", ""),
            getattr(p, "is_active", ""),
            total_stock,
        ])

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
        .order_by("-created_at")
    )

    for m in movements:
        if hasattr(m, "get_movement_type_display"):
            movement_type = m.get_movement_type_display()
        else:
            movement_type = m.movement_type

        writer.writerow([
            m.created_at.strftime("%Y-%m-%d %H:%M"),
            m.product.name if m.product_id else "",
            movement_type,
            m.quantity,
            m.warehouse_from.name if m.warehouse_from_id else "",
            m.warehouse_to.name if m.warehouse_to_id else "",
            m.user.username if m.user_id else "",
        ])

    return response

@login_required
def product_list(request):
    products = Product.objects.all().order_by("name")
    return render(request, "inventory/product_list.html", {"products": products})

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
