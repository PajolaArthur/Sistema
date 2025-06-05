from django.urls import path
from .views import (
    abrir_caixa, fechar_caixa, lancar_movimento, fechar_caixa_pdf, caixa_consulta,
    caixa_consulta_pdf,
    MovimentoListView, 
    FormapagamentoListView,FormapagamentoCreateView, FormapagamentoUpdateView, formapagamento_excluir
)

urlpatterns = [
    path('', MovimentoListView.as_view(), name='caixa'),
    path('abrir/', abrir_caixa, name='caixa-abrir'),
    path('fechar/', fechar_caixa, name='caixa-fechar'),
    path('lancamento/', lancar_movimento, name='caixa-lancamento'),
    path('fechar-caixa-pdf/', fechar_caixa_pdf, name='fechar-caixa-pdf'),
    path('consultas/', caixa_consulta, name='caixa-consulta'),
    path('consultas/pdf/', caixa_consulta_pdf, name='caixa-consulta-pdf'),
    path('formapagamento/', FormapagamentoListView.as_view(), name='formapagamento-list'),
    path('formapagamento/novo/', FormapagamentoCreateView.as_view(), name='formapagamento-create'),
    path('formapagamento/<int:pk>/editar/', FormapagamentoUpdateView.as_view(), name='formapagamento-edit'),
    path('formapagamento/<int:pk>/excluir/', formapagamento_excluir, name='formapagamento-delete'),


]
