from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.home, name='home'),
    # Categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),

    # Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.gestionar_producto, name='crear_producto'),
    
    path('productos/editar/<int:pk>/', views.gestionar_producto, name='editar_producto'),
    
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    
    # Pedidos
    path('listarpedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('nuevo/', views.crear_pedido, name='crear_pedido'),
    path('<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pk>/cambiar_estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('pedido/<int:pk>/ticket-pdf/', views.exportar_ticket_pdf, name='exportar_ticket_pdf'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
