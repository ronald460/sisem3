from django import forms
from .models import *



class solic_remi_form(forms.ModelForm):
    class Meta:
        model = solic_remi
        fields = ['nriu', 'cod_cast', 'name', 'document', 'direction', 'phone', 'period', 'date']

        widgets = {
            'nriu': forms.TextInput(attrs={'class': 'form-control'}),
            'cod_cast': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control'}),
            'direction': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }