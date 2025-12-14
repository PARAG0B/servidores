from django import forms
from .models import Movement


class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ["product", "warehouse", "movement_type", "quantity", "reference", "notes"]

