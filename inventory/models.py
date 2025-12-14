from django.db import models


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
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Stock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField("Cantidad", max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ("warehouse", "product")
        verbose_name = "Existencia"
        verbose_name_plural = "Existencias"

    def __str__(self):
        return f"{self.warehouse} | {self.product} -> {self.quantity}"


MOVEMENT_TYPES = (
    ("IN", "Entrada"),
    ("OUT", "Salida"),
    ("TR", "Transferencia"),
)


class Movement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(
    Warehouse,
    on_delete=models.PROTECT,
    null=True,
    blank=True,
)
    movement_type = models.CharField("Tipo", max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField("Cantidad", max_digits=12, decimal_places=2)
    created_at = models.DateTimeField("Fecha", auto_now_add=True)
    reference = models.CharField("Referencia", max_length=50, blank=True)
    notes = models.TextField("Notas", blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.quantity} {self.product} ({self.warehouse})"

