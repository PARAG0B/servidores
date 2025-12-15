from django import forms
from .models import Movement


class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ["warehouse", "product", "movement_type", "quantity", "reference", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["code", "name", "description", "min_stock", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
