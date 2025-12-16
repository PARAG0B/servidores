from django.core.management.base import BaseCommand

from inventory.models import Movement


class Command(BaseCommand):
    help = "Lista los últimos movimientos de inventario."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Número máximo de movimientos a mostrar (por defecto 20).",
        )

    def handle(self, *args, **options):
        limit = options["limit"]

        qs = Movement.objects.all().order_by("-id")[:limit]

        if not qs.exists():
            self.stdout.write(self.style.WARNING("No hay movimientos registrados."))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Últimos {qs.count()} movimientos:\n")
        )

        for m in qs:
            fecha = getattr(m, "created_at", None)
            fecha_str = fecha.strftime("%Y-%m-%d %H:%M") if fecha else "-"
            warehouse = getattr(m, "warehouse", None)
            product = getattr(m, "product", None)

            self.stdout.write(
                f"[{m.id}] {fecha_str} | "
                f"Bodega: {warehouse or '-'} | "
                f"Producto: {product or '-'} | "
                f"Tipo: {m.movement_type} | "
                f"Cantidad: {m.quantity}"
            )
