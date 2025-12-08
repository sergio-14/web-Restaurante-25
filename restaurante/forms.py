from decimal import Decimal
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Pedido, DetallePedido, Producto

from django import forms
from .models import Categoria, Producto

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['tipo', 'estado', 'mesa', 'cliente_nombre']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'mesa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº de mesa (si aplica)'}),
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
        }

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
       
        if tipo == Pedido.TipoPedido.LLEVAR:
            cleaned['mesa'] = None
        return cleaned


class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control producto-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned = super().clean()
        producto = cleaned.get('producto')
        precio_unitario = cleaned.get('precio_unitario')
        cantidad = cleaned.get('cantidad') or 1

        if not producto:
            raise ValidationError("Seleccione un producto.")

        if precio_unitario is None or Decimal(precio_unitario) == Decimal('0'):
           
            cleaned['precio_unitario'] = producto.precio

      
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        return cleaned

DetallePedidoFormSet = inlineformset_factory(
    Pedido,
    DetallePedido,
    form=DetallePedidoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
