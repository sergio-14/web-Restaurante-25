from django.contrib import admin
from .models import Categoria, Producto, Pedido, DetallePedido
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
# Register your models here.
