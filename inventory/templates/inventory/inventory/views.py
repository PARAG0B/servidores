# inventory/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from .models import Stock, Movement


@login_required
def dashboard(request):
    # 1) Totales por producto (para la primera tabla)
    totals = (
        Stock.objects
        .values('product__name')
        .annotate(total=Sum('quantity'))
        .order_by('product__name')
    )

    # 2) Detalle por bodega (para la segunda tabla)
    stocks = (
        Stock.objects
        .select_related('warehouse', 'product')
        .order_by('warehouse__name', 'product__name')
    )

    context = {
        "totals": totals,
        "stocks": stocks,
    }
    return render(request, "inventory/dashboard.html", context)
