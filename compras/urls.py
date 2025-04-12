from django.urls import path
from .views import (
    CompraListView, CompraCreateView, CompraUpdateView,
    CompraDeleteView, aprovar_compra, recusar_compra, excluir_compra
)

urlpatterns = [
    path('', CompraListView.as_view(), name='compra-list'),
    path('create/', CompraCreateView.as_view(), name='compra-create'),
    path('<int:pk>/edit/', CompraUpdateView.as_view(), name='compra-edit'),
    path('<int:pk>/delete/', CompraDeleteView.as_view(), name='compra-delete'),
    path('<int:pk>/aprovar/', aprovar_compra, name='compra-aprovado'),
    path('<int:pk>/recusar/', recusar_compra, name='compra-recusado'),
    path('<int:pk>/excluir/', excluir_compra, name='excluir-compra'),
]
