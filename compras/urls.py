from django.urls import path
from .views import (
    CompraListView, CompraCreateView, CompraUpdateView,
    CompraDeleteView, aprovar_compra, recusar_compra, compra_excluir,
    gerar_pdf_compras
)
from .views import FabricanteListView, FabricanteCreateView, FabricanteUpdateView, excluir_fabricante
from .views import CategoriaListView, CategoriaCreateView, CategoriaUpdateView, excluir_categoria

urlpatterns = [
    path('', CompraListView.as_view(), name='compra-list'),
    path('create/', CompraCreateView.as_view(), name='compra-create'),
    path('<int:pk>/edit/', CompraUpdateView.as_view(), name='compra-edit'),
    path('<int:pk>/delete/', CompraDeleteView.as_view(), name='compra-delete'),
    path('<int:pk>/aprovar/', aprovar_compra, name='compra-aprovado'),
    path('<int:pk>/recusar/', recusar_compra, name='compra-recusado'),
    path('<int:pk>/excluir/', compra_excluir, name='compra-excluir'),
    path('pdf/', gerar_pdf_compras, name='compras-pdf'),
    path('fabricantes/', FabricanteListView.as_view(), name='fabricante-list'),
    path('fabricantes/novo/', FabricanteCreateView.as_view(), name='fabricante-create'),
    path('fabricantes/<int:pk>/editar/', FabricanteUpdateView.as_view(), name='fabricante-edit'),
    path('fabricantes/<int:pk>/excluir/', excluir_fabricante, name='fabricante-delete'),
    path('categorias/', CategoriaListView.as_view(), name='categoria-list'),
    path('categorias/novo/', CategoriaCreateView.as_view(), name='categoria-create'),
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria-edit'),
    path('categorias/<int:pk>/excluir/', excluir_categoria, name='categoria-delete'),
]
