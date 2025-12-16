from django import forms
from .models import Product, Movement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Usamos TODOS los campos del modelo, sin inventar nombres.
        fields = "__all__"


class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        # De momento usamos __all__ para no adivinar campos.
        # Luego si hace falta afinamos.
        fields = "__all__"
