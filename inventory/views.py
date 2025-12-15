from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models import Sum
import csv
from django.http import HttpResponse
from .models import Stock, Movement
from .forms import MovementForm
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import Product, Movement

@login_required
def dashboard(request):
    totals = (
        Stock.objects
        .select_related("product")
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("product__name")
    )
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
        .order_by("-created_at")[:100]
    )
    return render(request, "inventory/movement_list.html", {"movements": movements})


@login_required
def movement_create(request):
    if request.method == "POST":
        form = MovementForm(request.POST)
        if form.is_valid():
            try:
                movement = form.save()  # aquí se ejecuta el save() con lógica de stock
            except ValidationError as e:
                # Errores de negocio (stock insuficiente, etc.)
                form.add_error(None, e.message)
            else:
                messages.success(request, "Movimiento registrado correctamente.")
                return redirect("inventory:movement_list")
    else:
        form = MovementForm()

    return render(request, "inventory/movement_form.html", {"form": form})

@login_required
def movement_export_csv(request):
    """
    Exporta los últimos movimientos a un archivo CSV.
    """
    # Creamos la respuesta HTTP con tipo CSV
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="movimientos_inventrack.csv"'

    writer = csv.writer(response)

    # Encabezados
    writer.writerow([
        "ID",
        "Fecha / Hora",
        "Tipo",
        "Bodega",
        "Producto",
        "Cantidad",
        "Referencia",
        "Notas",
        "Usuario",
    ])

    # Traemos los movimientos (puedes limitar a 1000 si quieres)
    movements = (
        Movement.objects
        .select_related("warehouse", "product")
        .order_by("-created_at")
    )

    for m in movements:
        writer.writerow([
            m.id,
            m.created_at.strftime("%Y-%m-%d %H:%M"),
            m.get_movement_type_display(),
            m.warehouse.name if hasattr(m.warehouse, "name") else str(m.warehouse),
            m.product.name if hasattr(m.product, "name") else str(m.product),
            m.quantity,
            m.reference or "",
            (m.notes or "").replace("\n", " "),  # sin saltos de línea
            m.created_by.username if hasattr(m, "created_by") and m.created_by else "",
        ])

    return response

@login_required
def product_list(request):
    """
    Lista simple de productos. Desde aquí se podrá entrar al historial
    de cada producto.
    """
    products = Product.objects.all().order_by("name")
    context = {
        "products": products,
    }
    return render(request, "inventory/product_list.html", context)


@login_required
def product_detail(request, pk):
    """
    Historial por producto: muestra la info del producto y
    todos los movimientos asociados.
    """
    product = get_object_or_404(Product, pk=pk)

    # Ordenamos por id descendente (id siempre existe)
    movements = (
        Movement.objects
        .filter(product=product)
        .order_by("-id")
    )

    context = {
        "product": product,
        "movements": movements,
    }
    return render(request, "inventory/product_detail.html", context)
