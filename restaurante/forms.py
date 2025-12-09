from decimal import Decimal
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Pedido, DetallePedido, Producto, Categoria

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        self.fields['producto'].required = False
        self.fields['cantidad'].required = False
        self.fields['precio_unitario'].required = False

    def clean(self):
        cleaned = super().clean()
        producto = cleaned.get('producto')
        precio_unitario = cleaned.get('precio_unitario')
        cantidad = cleaned.get('cantidad')

       
        if not producto:
            
            if cantidad or precio_unitario:
                raise ValidationError("Debe seleccionar un producto.")
     
            return cleaned

        if not cantidad or cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

      
        if precio_unitario is None or Decimal(precio_unitario) == Decimal('0'):
            cleaned['precio_unitario'] = producto.precio

        return cleaned

class DetallePedidoBaseFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        
        
        formularios_validos = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
          
            if form.cleaned_data.get('producto'):
                formularios_validos += 1
        
        if formularios_validos < 1:
            raise ValidationError('Debe agregar al menos un producto al pedido.')


DetallePedidoFormSet = inlineformset_factory(
    Pedido,
    DetallePedido,
    form=DetallePedidoForm,
    formset=DetallePedidoBaseFormSet,
    extra=1,
    can_delete=True,
    validate_min=False,  
)