from django.urls import path
from .views import (
    abrir_caixa, fechar_caixa, lancar_movimento, fechar_caixa_pdf, caixa_consulta,
    MovimentoListView
)

urlpatterns = [
    path('', MovimentoListView.as_view(), name='caixa'),
    path('abrir/', abrir_caixa, name='caixa-abrir'),
    path('fechar/', fechar_caixa, name='caixa-fechar'),
    path('lancamento/', lancar_movimento, name='caixa-lancamento'),
    path('fechar-caixa-pdf/', fechar_caixa_pdf, name='fechar-caixa-pdf'),
    path('consultas/', caixa_consulta, name='caixa-consulta'),

]
