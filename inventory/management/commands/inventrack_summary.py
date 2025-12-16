from django.core.management.base import BaseCommand
from django.db.models import Sum

from inventory.models import Stock


class Command(BaseCommand):
    help = "Muestra un resumen de existencias por producto y por bodega."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("== Resumen de existencias =="))

        # Totales por producto
        self.stdout.write("\nTotales por producto:")
        totals = (
            Stock.objects
            .select_related("product")
            .values("product__id", "product__name")
            .annotate(total=Sum("quantity"))
            .order_by("product__name")
        )

        if not totals:
            self.stdout.write("  (sin datos de stock)")
        else:
            for item in totals:
                self.stdout.write(
                    f"  - {item['product__name']} (ID {item['product__id']}): {item['total']}"
                )

        # Detalle por bodega
        self.stdout.write("\nDetalle por bodega:")
        stocks = (
            Stock.objects
            .select_related("warehouse", "product")
            .all()
            .order_by("warehouse__name", "product__name")
        )

        if not stocks:
            self.stdout.write("  (sin datos de stock)")
        else:
            for s in stocks:
                self.stdout.write(
                    f"  - Bodega: {s.warehouse} | Producto: {s.product} | Cantidad: {s.quantity}"
                )
