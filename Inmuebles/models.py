from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class calculations(models.Model):
    id = models.AutoField(primary_key=True)
    cod_sap = models.CharField(max_length=20, blank=True, null=True)
    cod_cast = models.CharField(max_length=50, blank=False, null=False)
    sector = models.CharField(max_length=50, blank=True, null=True)
    typology = models.CharField(max_length=50, blank=True, null=True)
    typology_2 = models.CharField(max_length=50, blank=True, null=True)
    m_sector = models.CharField(max_length=50, blank=True, null=True)
    m_typo = models.CharField(max_length=50, blank=True, null=True)
    m_typo_2 = models.CharField(max_length=50, blank=True, null=True)
    period = models.CharField(max_length=20, blank=False, null=False)
    tax = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
    surcharges = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
    interests = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
    penalty = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.cod_sap
    
    class Meta:
        db_table = 'inm_calculations'
        verbose_name = 'Calculation'
        verbose_name_plural = 'Calculations'


class tipologia(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    period = models.CharField(max_length=20, blank=False, null=False)
    value = models.DecimalField(max_digits=15, decimal_places=4, blank=False, null=False)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'inm_tipologia'
        verbose_name = 'Tipologia'
        verbose_name_plural = 'Tipologias'

class sector(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(max_length=50, blank=False, null=False)
    period = models.CharField(max_length=20, blank=False, null=False)
    value = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'inm_sector'
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectors'

class tasas_interes(models.Model):
    id = models.AutoField(primary_key=True)
    mes = models.IntegerField()
    ano = models.IntegerField()
    value = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)

    def __str__(self):
        return str(self.mes) + ' ' + str(self.ano)
    
    class Meta:
        db_table = 'inm_tasas_interes'
        verbose_name = 'Tasa de Interes'
        verbose_name_plural = 'Tasas de Interes'


class solic_calc(models.Model):
    id = models.AutoField(primary_key=True)
    cod_cast = models.CharField(max_length=50, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    document = models.CharField(max_length=20, blank=False, null=False)
    direction = models.CharField(max_length=200, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'inm_solic_calc'
        verbose_name = 'Solicitud de Calculo'
        verbose_name_plural = 'Solicitudes de Calculo'

class solic_remi(models.Model):
    id = models.AutoField(primary_key=True)
    nriu = models.CharField(max_length=20, blank=False, null=False, unique=True)
    cod_cast = models.CharField(max_length=50, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    document = models.CharField(max_length=20, blank=False, null=False)
    direction = models.CharField(max_length=200, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)
    period = models.CharField(max_length=100, blank=False, null=False)
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'inm_solic_remi'
        verbose_name = 'Solicitud de Remision'
        verbose_name_plural = 'Solicitudes de Remision'