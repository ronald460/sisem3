from django.db import models
from Administracion.models import *
from django.contrib.auth.models import User

class Bienes (models.Model):
    id = models.AutoField(primary_key=True)
    bm = models.CharField(max_length=200, unique=True, blank=False)
    description = models.TextField(max_length=500, blank=True)
    serial = models.CharField (max_length=250, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=100, blank=True, null=True)
    part = models.CharField(blank=True, null=True, max_length=20)  # Ej: "0/4"
    select_a = (
        ('Bueno', 'Bueno'),
        ('Dañado', 'Dañado'),    
    )
    status = models.CharField(max_length=50, choices=select_a, default='Bueno')
    select_b = (
        ('Completo', 'Completo'),
        ('Incompleto', 'Incompleto'),
    )
    condition = models.CharField(max_length=50, choices=select_b, default='Completo')
 
    class Meta:
        db_table = 'bienes'
        ordering = ['-bm']

    def __str__(self):
        return f"Bien #{self.bm} - ({self.description})"
    

class Bienes_persona(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False)
    id_worker = models.ForeignKey(Empleado, on_delete=models.CASCADE, max_length=20, blank=True)
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, max_length=20, blank=True)
    bm_worker = models.CharField(max_length=100, blank=True)
    serial = models.CharField(max_length=100, blank=True)
    description = models.CharField (max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=50, blank=True)
    signature = models.FileField(upload_to ='Firma_persona/',  blank=True, null=True)
    observation = models.CharField(max_length=100, blank=True, null=True)
    estatus = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bienes_persona'
        ordering = ['-id']

    def __str__(self):
        return f"Bien #{self.bm_worker} - ({self.description})"


class Bienes_movimientos (models.Model):
    id = models.AutoField(primary_key=True)
    transfer_date = models.DateField()
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, max_length=20, blank=True)
    description = models.CharField (max_length=200, blank=True)
    mov_choices = (
        ('Transfer', 'Traslado'),
        ('Return', 'Devolucion'),
        ('Assignment', 'Asignacion'),
        
    )
    mov_type = models.CharField(max_length=50, choices=mov_choices, default='Transfer') 
    type_choices = (
        ('Personal', 'Personal'),
        ('EntePublico', 'EntePublico'),
        
    )
    Type = models.CharField(max_length=50, choices=type_choices, default='Personal')
    origin_entity = models.CharField (max_length=200, blank=True)
    origin_area = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False)
    id_worker = models.ForeignKey(Empleado, on_delete=models.CASCADE, max_length=20, blank=True)
    rif_ente = models.CharField (max_length=100, blank=True)
    nomb_respon_ant = models.CharField (max_length=100, blank=True)
    dest_entity = models.CharField (max_length=200, blank=True)
    dest_area = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False, related_name='dest_area')
    id_worker_tow = models.ForeignKey(Empleado, on_delete=models.CASCADE, max_length=20, blank=True, related_name='id_worker_tow')
    worker = models.CharField (max_length=100, blank=True)
    observation = models.CharField (max_length=100, blank=True) 
    condition_choices = (
        ('good', 'Bueno'),
        ('damaged', 'Dañado'),    
    )
    condition = models.CharField(max_length=50, choices=condition_choices, default='good')
    status = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bienes_movimientos'
        ordering = ['-transfer_date']

    def __str__(self):
        return f"Movimiento de Bien #{self.id_bien} - ({self.description})"
    

class Bienes_informes (models.Model):
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False)
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, max_length=20, blank=True)
    date = models.DateField()
    description = models.CharField (max_length=200, blank=True)
    diagnosis = models.CharField (max_length=300, blank=True)
    signature = models.FileField(upload_to ='Firma_Informe/',  blank=True)
    status = models.BooleanField()

    class Meta:
        db_table = 'bienes_informes'
        ordering = ['-date']

    def __str__(self):
        return f"Informe de Bien #{self.id_bien} - ({self.description})"
    

class otros_bienes(models.Model):
    id = models.AutoField(primary_key=True)
    bm = models.CharField(max_length=200, unique=True, blank=False)
    description = models.TextField(max_length=500, blank=True)
    area = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False)
    observation = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'otros_bienes'
        ordering = ['-id']

    def __str__(self):
        return f"Otro Bien #{self.id} - ({self.description})"
    

class encargado_bienes(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False)
    id_worker = models.ForeignKey(User, on_delete=models.CASCADE, max_length=100)
    signature = models.FileField(upload_to ='Firma_Encargado/',  blank=True, null=True)
    observation = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'encargado_bienes'
        ordering = ['-id']

    def __str__(self):
        return f"Encargado de Bienes #{self.id_worker} - ({self.area.name})"


class otros_bienes_pd(models.Model):
    id = models.AutoField(primary_key=True)
    bm = models.CharField(max_length=200, unique=True, blank=False)
    description = models.TextField(max_length=500, blank=True)
    serial = models.CharField(max_length=100, blank=True)
    id_worker = models.ForeignKey(Empleado, on_delete=models.CASCADE, max_length=20, blank=True)
    area = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=False)
    condition = models.CharField(max_length=50, blank=True)
    observation = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'otros_bienes_pd'
        ordering = ['-id']

    def __str__(self):
        return f"Otro Bien #{self.id} - ({self.description})"
    