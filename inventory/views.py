from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models import Sum

from .models import Stock, Movement
from .forms import MovementForm


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

