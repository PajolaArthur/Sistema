from django.urls import path
from .views import (
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
    cliente_excluir,
    carregar_municipios
)



urlpatterns = [
    path('', ClienteListView.as_view(), name='cliente-list'),
    path('novo/', ClienteCreateView.as_view(), name='cliente-create'),
    path('<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente-edit'),
    path('<int:pk>/deletar/', ClienteDeleteView.as_view(), name='cliente-delete'),
    path('<int:pk>/excluir/', cliente_excluir, name='cliente-excluir'),
    path('carregar_municipios/', carregar_municipios, name='carregar_municipios'),

]
