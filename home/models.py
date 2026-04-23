from django.db import models

# Create your models here.


class euro(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.valor
    
    class Meta:
        verbose_name = 'Euro'
        verbose_name_plural = 'Euros'
        db_table = 'euro'
    
class dolar(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.valor
    
    class Meta:
        verbose_name = 'Dolar'
        verbose_name_plural = 'Dolares'
        db_table = 'dolar'


class Reporte(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    url = models.CharField(max_length=200)
    activo = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        db_table = 'reporte'