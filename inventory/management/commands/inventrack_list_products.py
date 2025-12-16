from django.core.management.base import BaseCommand
from django.db.models import Sum

from inventory.models import Product, Stock


class Command(BaseCommand):
    help = "Lista todos los productos con su stock total en todas las bodegas."

    def handle(self, *args, **options):
        products = Product.objects.all().order_by("name")

        if not products.exists():
            self.stdout.write(self.style.WARNING("No hay productos registrados."))
            return

        self.stdout.write(self.style.SUCCESS("Listado de productos:\n"))

        for p in products:
            total = (
                Stock.objects.filter(product=p)
                .aggregate(total=Sum("quantity"))
                .get("total")
                or 0
            )
            self.stdout.write(f"- ID {p.id} | {p.name} | Stock total: {total}")
