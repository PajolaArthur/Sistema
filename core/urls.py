from django.contrib import admin
from django.urls import path, include
from .views import Home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('compras/', include('compras.urls')),
    path('caixa/', include('caixa.urls')),
    path('controle_acesso/', include('controle_acesso.urls')),
]
