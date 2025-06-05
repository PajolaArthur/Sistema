from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('compras/', include('compras.urls')),
    path('caixa/', include('caixa.urls')),
    path('cliente/', include('cliente.urls')),
    path('controle_acesso/', include('controle_acesso.urls')),
]
