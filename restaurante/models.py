from django.db import models
from django.utils.translation import gettext_lazy as _

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Categoría")
        verbose_name_plural = _("Categorías")

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")

    def __str__(self):
        return f"{self.nombre} ({self.precio} Bs.)"


class Pedido(models.Model):

    class TipoPedido(models.TextChoices):
        MESA = "MESA", _("En mesa")
        LLEVAR = "LLEVAR", _("Para llevar")

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", _("Pendiente")
        PREPARANDO = "PREPARANDO", _("Preparando")
        ENTREGADO = "ENTREGADO", _("Entregado")
        CANCELADO = "CANCELADO", _("Cancelado")

    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(
        max_length=20,
        choices=TipoPedido.choices,
        default=TipoPedido.MESA
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    mesa = models.CharField(max_length=20, blank=True, null=True)
    cliente_nombre = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")

    def __str__(self):
        return f"Pedido #{self.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    @property
    def total(self):
        return sum(det.subtotal for det in self.detalles.all())

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Detalle de Pedido")
        verbose_name_plural = _("Detalles del Pedido")

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
