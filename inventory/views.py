from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

from .models import Stock, Movement
from .forms import MovementForm


@login_required
def dashboard(request):
    """Vista principal: muestra existencias y totales por producto."""
    stocks = (
        Stock.objects
        .select_related("product", "warehouse")
        .order_by("product__name", "warehouse__name")
    )

    totals = (
        Stock.objects
        .values("product__id", "product__name")
        .annotate(total=Sum("quantity"))
        .order_by("product__name")
    )

    context = {
        "stocks": stocks,
        "totals": totals,
    }
    return render(request, "inventory/dashboard.html", context)


@login_required
def movement_list(request):
    """Lista los últimos movimientos de inventario."""
    movements = (
        Movement.objects
        .select_related("product", "warehouse")
        .order_by("-created_at")[:100]
    )
    return render(request, "inventory/movement_list.html", {"movements": movements})


@login_required
def movement_create(request):
    """Crea un nuevo movimiento y actualiza el Stock."""
    if request.method == "POST":
        form = MovementForm(request.POST)
        if form.is_valid():
            movement = form.save()

            stock, _ = Stock.objects.get_or_create(
                product=movement.product,
                warehouse=movement.warehouse,
                defaults={"quantity": 0},
            )

            if movement.movement_type == "IN":
                stock.quantity += movement.quantity
            elif movement.movement_type == "OUT":
                stock.quantity -= movement.quantity
            # Luego podemos manejar transferencias (TR)

            stock.save()
            return redirect("inventory:movement_list")
    else:
        form = MovementForm()

    return render(request, "inventory/movement_form.html", {"form": form})

