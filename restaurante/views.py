from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.contrib import messages

from .models import Pedido, Producto
from .forms import PedidoForm, DetallePedidoFormSet

from .models import Categoria, Producto
from .forms import CategoriaForm, ProductoForm

# ----- Categoría -----
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias/lista_categorias.html', {'categorias': categorias})

def crear_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada correctamente")
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'categorias/crear_categoria.html', {'form': form})

# ----- Producto -----
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista_productos.html', {'productos': productos})

def gestionar_producto(request, pk=None):

    is_editing = pk is not None
    
  
    producto = get_object_or_404(Producto, pk=pk) if is_editing else Producto()
    
    if request.method == "POST":
       
        form = ProductoForm(request.POST, instance=producto)
        
        if form.is_valid():
            form.save()
            if is_editing:
                messages.success(request, f"Producto '{producto.nombre}' actualizado correctamente.")
            else:
                messages.success(request, f"Producto '{producto.nombre}' creado correctamente.")
            return redirect('lista_productos')
    else:
        
        form = ProductoForm(instance=producto)
        
    context = {
        'form': form,
        'is_editing': is_editing, 
        'producto': producto,
    }
 
    return render(request, 'productos/crear_producto.html', context)


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f"Producto '{nombre_producto}' eliminado correctamente.")
        return redirect('lista_productos')
    
    
    return render(request, 'productos/confirmar_eliminar.html', {'producto': producto})

import logging


logger = logging.getLogger(__name__)

# ----- Pedido -----
def crear_pedido(request):
    productos = Producto.objects.filter(activo=True)

    if request.method == 'POST':
        form = PedidoForm(request.POST)

        if form.is_valid():
            pedido = form.save(commit=False)
            formset = DetallePedidoFormSet(request.POST, instance=pedido)
        else:
            formset = DetallePedidoFormSet(request.POST)

        is_fs_valid = formset.is_valid()

        if form.is_valid() and is_fs_valid:
            try:
                with transaction.atomic():
                    pedido.save()

                    detalles = formset.save(commit=False)
                    detalles_validos = [det for det in detalles if getattr(det, 'producto', None)]

                    if not detalles_validos:
                        messages.error(request, "Debe agregar al menos un producto al pedido.")
                        raise ValueError("No hay productos en el pedido")

                    for det in detalles_validos:
                        det.pedido = pedido
                        det.save()

                    for det_del in formset.deleted_objects:
                        det_del.delete()

                    messages.success(request, f"Pedido #{pedido.id} creado correctamente. Total: Bs{pedido.total}")
                    return redirect(reverse('detalle_pedido', args=[pedido.id]))

            except Exception as e:
                # Registrar el error y mostrar mensaje al usuario
                logger.exception("Error al guardar el pedido")
                messages.error(request, f"Error al guardar el pedido: {e}")
        else:
            # Mostrar errores al usuario
            if not form.is_valid():
                messages.error(request, f"Errores en el formulario: {form.errors}")
            if not is_fs_valid:
                messages.error(request, f"Errores en los detalles: {formset.errors}")

    else:
        form = PedidoForm()
        formset = DetallePedidoFormSet()

    return render(request, 'pedidos/order_form.html', {
        'form': form,
        'formset': formset,
        'productos': productos,
        'is_create': True,
    })


def cambiar_estado_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == "POST":
        nuevo_estado = request.POST.get("nuevo_estado")
        if nuevo_estado in [Pedido.Estado.ENTREGADO, Pedido.Estado.CANCELADO]:
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f"Estado actualizado a {nuevo_estado}")
        else:
            messages.error(request, "Estado no válido")

    return redirect('lista_pedidos')

def detalle_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    return render(request, 'pedidos/order_detail.html', {'pedido': pedido})


from django.db.models import F, Sum, DecimalField 
from .models import Pedido 

def lista_pedidos(request):
    estado_filtro = request.GET.get('estado')
    
    qs = Pedido.objects.all().order_by('-fecha')
    
    if estado_filtro and estado_filtro != 'TODOS':
        qs = qs.filter(estado=estado_filtro)
    
    total_registros = qs.count()

    ganancia_total = sum(pedido.total for pedido in qs)

    
    context = {
        'pedidos': qs,
        'estados_choices': Pedido.Estado.choices,
        'estado_seleccionado': estado_filtro if estado_filtro else 'TODOS',
        'total_registros': total_registros,
        'ganancia_total': ganancia_total, 
    }
    return render(request, 'pedidos/listar_pedidos.html', context)


def home(request):
    return render(request, 'dashboard.html')
