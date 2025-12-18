from django.db import models
from django.db import models, transaction
from django.core.exceptions import ValidationError


class Warehouse(models.Model):
    name = models.CharField("Nombre", max_length=100)
    code = models.CharField(
    "Código",
    max_length=10,
    unique=True,
    null=True,
    blank=True,
)
    location = models.CharField("Ubicación", max_length=200, blank=True)
    is_active = models.BooleanField("Activa", default=True)

    class Meta:
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(models.Model):
    sku = models.CharField(
        "SKU",
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )
    name = models.CharField("Nombre", max_length=150)
    unit = models.CharField("Unidad", max_length=20, default="und")

    # ✅ NUEVO: stock mínimo para alerta
    min_stock = models.PositiveIntegerField(
        "Stock mínimo",
        default=0,
        help_text="Cuando el stock total esté por debajo de este valor, se genera alerta."
    )

    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.sku} - {self.name}"



class Stock(models.Model):
    warehouse = models.ForeignKey("Warehouse", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ("warehouse", "product")

    def __str__(self):
        return f"{self.warehouse} - {self.product} ({self.quantity})"


class Movement(models.Model):
    IN = "IN"
    OUT = "OUT"
    MOVEMENT_TYPES = [
        (IN, "Entrada"),
        (OUT, "Salida"),
    ]

    warehouse = models.ForeignKey("Warehouse", on_delete=models.PROTECT)
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.quantity} de {self.product} en {self.warehouse}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Solo aplicamos el movimiento al stock cuando es nuevo
        if is_new:
            # Bloqueamos/fijamos la fila de stock correspondiente
            stock, created = Stock.objects.select_for_update().get_or_create(
                warehouse=self.warehouse,
                product=self.product,
                defaults={"quantity": 0},
            )

            if self.movement_type == self.OUT:
                # Validar que haya suficiente stock
                if stock.quantity < self.quantity:
                    raise ValidationError(
                        f"No hay stock suficiente en {self.warehouse} para sacar {self.quantity} unidades. "
                        f"Stock actual: {stock.quantity}."
                    )
                stock.quantity -= self.quantity
            else:
                # Entrada
                stock.quantity += self.quantity

            stock.save()

        super().save(*args, **kwargs)
