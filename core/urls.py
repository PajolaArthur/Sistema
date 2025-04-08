from django.contrib import admin
from django.urls import path, include
#from compras.views import compra_list
from compras.views import CompraListView
from compras.views import CompraUpdateView
from compras.views import CompraDeleteView
from compras.views import CompraCreateView
from compras.views import aprovar_compra
from compras.views import recusar_compra


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('',compra_list),
    path('',CompraListView.as_view(), name = 'compra-list'),
    path('compras/<int:pk>/edit/',CompraUpdateView.as_view(), name = 'compra-edit'),
    path('compras/<int:pk>/delete/',CompraDeleteView.as_view(), name = 'compra-delete'),
    path('compras/create/',CompraCreateView.as_view(), name = 'compra-create'),
    path('compras/<int:pk>/aprovar/', aprovar_compra, name='compra-aprovado'),
    path('compras/<int:pk>/recusar/', recusar_compra, name='compra-recusado'),
    path('controle_acesso/',include('controle_acesso.urls')),
]
