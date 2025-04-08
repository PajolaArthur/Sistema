from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import CreateView
from .models import Compra
from .forms import CompraForm
from .forms import CompraFormCreate
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
import datetime
from django.shortcuts import get_object_or_404, redirect


#def compra_list(request):
#    compras = Compra.objects.all()
#    return render(request,'compra_list.html',{'compras':compras})

@method_decorator(login_required, name="dispatch")
class CompraListView(ListView):
    model = Compra
    template_name = 'compra_list.html'
    #paginate_by = 10
    context_object_name = 'compras'

    def get_queryset(self):
        queryset = super().get_queryset()

        compras = self.request.GET.get('q', '').strip()
        codigoproduto = self.request.GET.get('codigoproduto', '').strip()
        fabricante = self.request.GET.get('fabricante', '').strip()
        categoria = self.request.GET.get('categoria', '')
        data_inicial = self.request.GET.get('data_inicial')
        data_final = self.request.GET.get('data_final')

        filtros = Q()

        # Termo de busca geral
        if compras:
            filtros &= (
                Q(descricao_produto__icontains=compras) |
                Q(codigo_produto__icontains=compras) |
                Q(fabricante_produto__icontains=compras) |
                Q(categoria_produto__icontains=compras) |
                Q(situacao__icontains=compras)
            )

        # Filtro por nome do fabricante
        #if fabricante:
            #filtros &= Q(fabricante_produto__icontains=fabricante)

        if codigoproduto:
            filtros &= Q(codigo_produto__icontains=codigoproduto)

        if categoria:
            queryset = queryset.filter(categoria_produto=categoria)

        if fabricante:
            queryset = queryset.filter(fabricante_produto=fabricante)

        # Filtro por intervalo de datas
        try:
            if data_inicial:
                data_ini = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
                filtros &= Q(criado_em__date__gte=data_ini)
            if data_final:
                data_fim = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()
                filtros &= Q(criado_em__date__lte=data_fim)
        except ValueError:
            pass

        return queryset.filter(filtros)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['compra'] = Compra  # Passa o model para acessar CATEGORIAS no template
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fabricante_selecionado'] = self.request.GET.get('fabricante', '')
        context['compra'] = Compra  # Passa o model para acessar FABRICANTES no template
        return context
    
    
    



class CompraUpdateView(UpdateView):
    model = Compra
    form_class = CompraForm
    template_name = 'compra_edit.html'
    success_url = reverse_lazy('compra-list')
    def form_valid(self,form):
        #adicionar lógica no que o usuário escreveu no formulário
        return super().form_valid(form)
    
class CompraDeleteView(DeleteView):
    model = Compra
    template_name = 'compra_delete.html'
    success_url = reverse_lazy('compra-list')

class CompraCreateView(CreateView):
    model = Compra
    form_class = CompraFormCreate
    template_name = 'compra_create.html'
    success_url = reverse_lazy('compra-list')
    def form_valid(self,form):
        #adicionar lógica no que o usuário escreveu no formulário
        return super().form_valid(form)
    
def aprovar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    compra.situacao = 'A'  # 'A' de Aprovado
    compra.save()
    return redirect('compra-list')  # redireciona de volta para a listagem

def recusar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    compra.situacao = 'R'  # 'R' de Recusado
    compra.save()
    return redirect('compra-list')  # redireciona de volta para a listagem