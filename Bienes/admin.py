from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Bienes)
admin.site.register(Bienes_persona)
admin.site.register(encargado_bienes)
admin.site.register(otros_bienes_pd)
admin.site.register(otros_bienes_ci)