from django import forms
from .models import Movement


class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ["warehouse", "product", "movement_type", "quantity", "reference", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

