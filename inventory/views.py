from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import csv

from .models import Stock, Movement, Product
from .forms import MovementForm, ProductForm

@login_required
def dashboard(request):
    # Totales por producto (tabla 1)
    totals = (
        Stock.objects
        .select_related("product")
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("product__name")
    )

    # Detalle por bodega (tabla 2)
    stocks = (
        Stock.objects
        .select_related("warehouse", "product")
        .all()
        .order_by("warehouse__name", "product__name")
    )

    context = {
        "totals": totals,
        "stocks": stocks,
    }
    return render(request, "inventory/dashboard.html", context)

from django.http import HttpResponse  # asegúrate de que este import esté arriba


@login_required
def movement_list(request):
    return HttpResponse("Movements OK (vista de prueba)")
 

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
def movement_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="movimientos.csv"'

    writer = csv.writer(response)
    writer.writerow(["Fecha", "Bodega", "Producto", "Tipo", "Cantidad", "Referencia", "Usuario"])

    qs = (
        Movement.objects
        .select_related("warehouse", "product", "user")
        .order_by("-created_at")
    )

    for m in qs:
        writer.writerow([
            m.created_at.strftime("%Y-%m-%d %H:%M"),
            m.warehouse.name if m.warehouse else "",
            m.product.name if m.product else "",
            m.get_movement_type_display(),
            m.quantity,
            m.reference or "",
            m.user.username if m.user else "",
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
