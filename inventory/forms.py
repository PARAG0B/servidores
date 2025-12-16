from django import forms
from .models import Product, Movement


class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
