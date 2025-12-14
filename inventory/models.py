from django.db import models
from django.contrib.auth.models import User


class Warehouse(models.Model):
    name = models.CharField("Nombre bodega", max_length=100)
    location = models.CharField("Ubicación", max_length=150, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    code = models.CharField("Código", max_length=50, unique=True)
    name = models.CharField("Nombre", max_length=150)
    description = models.TextField("Descripción", blank=True)
    unit = models.CharField("Unidad de medida", max_length=20, default="UN")
    min_stock = models.PositiveIntegerField("Stock mínimo", default=0)
    is_active = models.BooleanField("Activo", default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Stock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="Bodega")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.IntegerField("Cantidad", default=0)

    class Meta:
        unique_together = ('warehouse', 'product')
        verbose_name = "Existencia"
        verbose_name_plural = "Existencias"

    def __str__(self):
        return f"{self.product} en {self.warehouse}: {self.quantity}"


class Movement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
        ('TR', 'Transferencia'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Producto")
    warehouse_from = models.ForeignKey(
        Warehouse,
        related_name='movements_from',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Bodega origen",
    )
    warehouse_to = models.ForeignKey(
        Warehouse,
        related_name='movements_to',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Bodega destino",
    )
    movement_type = models.CharField("Tipo movimiento", max_length=3, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField("Cantidad")
    created_at = models.DateTimeField("Fecha", auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    note = models.CharField("Observación", max_length=255, blank=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product} - {self.quantity}"

