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

def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente")
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear_producto.html', {'form': form})
# ----- Pedido -----

def crear_pedido(request):
    productos = Producto.objects.filter(activo=True)
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        formset = DetallePedidoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    pedido = form.save(commit=False)
                    pedido.save()
                  
                    formset.instance = pedido
                    detalles = formset.save(commit=False)
                    for det in detalles:
                        det.pedido = pedido
                        det.save()
                    for det_del in formset.deleted_objects:
                        det_del.delete()
                    messages.success(request, f"Pedido #{pedido.id} creado correctamente. Total: Bs{pedido.total}")
                    return redirect(reverse('detalle_pedido', args=[pedido.id]))
            except Exception as e:
                messages.error(request, f"Error al guardar el pedido: {e}")
        else:
            
            if form.errors:
                messages.error(request, f"Errores en el formulario: {form.errors}")
            if formset.errors:
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


def lista_pedidos(request):
    qs = Pedido.objects.all().order_by('-fecha')
    return render(request, 'pedidos/listar_pedidos.html', {'pedidos': qs})


def home(request):
    return render(request, 'dashboard.html')
