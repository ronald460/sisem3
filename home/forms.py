from django import forms
from .models import *


class act_confidentiality_form(forms.ModelForm):
    class Meta:
        model = act_confidentiality
        fields = ['date', 'system', 'observations']

        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type':'date'}),
            'observations': forms.TextInput(attrs={'class': 'form-control'}),
            'system':forms.Select(attrs={'class': 'form-select'}),
        }