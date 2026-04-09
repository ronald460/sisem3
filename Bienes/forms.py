from django import forms
from .models import *

class addBien_form(forms.ModelForm):
    class Meta:
        model = Bienes_persona
        fields = ['area', 'id_worker', 'bm_worker', 'serial', 'description', 
                  'brand', 'condition', 'signature', 'observation']
        widgets = {
            'area': forms.Select(attrs={'class': 'form-select'}),
            'id_worker': forms.Select(attrs={'class': 'form-select', 'data-live-search': 'true'}),
            'bm_worker': forms.TextInput(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'observation': forms.TextInput(attrs={'class': 'form-control'}),
            'signature': forms.ClearableFileInput(attrs={'accept': 'image/*,.pdf'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

