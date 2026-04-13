from django.db import models
from django.db.models import Q

class RegistroManager(models.Manager):
    def obtener_siguiente_numero(self):
       
        disponible = self.filter(status=False).order_by('bm').first()
        
        if disponible:
            return disponible.bm
    
        ultimo = self.filter(status=True).order_by('-bm').first()
        
        if not ultimo:
            return "PD-00001"
        
        num = int(ultimo.bm.split('-')[1])
        siguiente_num = num + 1
        return f"PD-{siguiente_num:05d}"